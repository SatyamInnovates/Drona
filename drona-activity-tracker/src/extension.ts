import * as vscode from 'vscode';
import { randomUUID } from 'node:crypto';

const DEFAULT_SERVER_URL = 'http://127.0.0.1:8000';
const DEFAULT_IDLE_MINUTES = 5;
const FLUSH_INTERVAL_MS = 15_000;
const MAX_BATCH_MS = 60_000;

type ActivityBatch = {
    event_id: string;
    day: string;
    project: string;
    language: string;
    duration_ms: number;
};

let trackingEnabled = true;
let lastActivityAt = 0;
let lastTickAt = Date.now();
let pendingBatches: ActivityBatch[] = [];
let activeProject = '';
let activeLanguage = '';
let serverUnavailable = false;
let nextRetryAt = 0;
let hasLoggedServerError = false;
let flushing = false;
let statusItem: vscode.StatusBarItem;
let extensionContext: vscode.ExtensionContext;

function localDay(timestamp: number): string {
    const value = new Date(timestamp);
    const year = value.getFullYear();
    const month = String(value.getMonth() + 1).padStart(2, '0');
    const day = String(value.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
}

function getIdleTimeout(): number {
    const configured = vscode.workspace
        .getConfiguration('dronaActivityTracker')
        .get<number>('idleMinutes', DEFAULT_IDLE_MINUTES);
    return Math.min(30, Math.max(1, configured)) * 60_000;
}

function updateStatus(): void {
    if (!statusItem) return;
    if (!trackingEnabled) {
        statusItem.text = '$(debug-pause) Drona: Paused';
        statusItem.tooltip = 'Automatic coding time tracking is paused. Click to resume.';
    } else if (serverUnavailable) {
        statusItem.text = '$(warning) Drona: Server offline';
        statusItem.tooltip = 'Coding activity will sync when the Drona server is available.';
    } else if (Date.now() - lastActivityAt < getIdleTimeout() && activeProject) {
        statusItem.text = `$(pulse) Drona: ${activeProject}`;
        statusItem.tooltip = `Tracking ${activeLanguage} activity in ${activeProject}. Click to pause.`;
    } else {
        statusItem.text = '$(clock) Drona: Waiting';
        statusItem.tooltip = 'Waiting for a code edit. Click to pause automatic tracking.';
    }
}

function queueActivity(durationMs: number, timestamp: number): void {
    if (durationMs <= 0 || !activeProject || !activeLanguage) return;
    const day = localDay(timestamp);
    let remaining = Math.floor(durationMs);
    while (remaining > 0) {
        let batch = pendingBatches[pendingBatches.length - 1];
        if (!batch || batch.day !== day || batch.project !== activeProject ||
            batch.language !== activeLanguage || batch.duration_ms >= MAX_BATCH_MS) {
            batch = {
                event_id: randomUUID(),
                day,
                project: activeProject,
                language: activeLanguage,
                duration_ms: 0,
            };
            pendingBatches.push(batch);
        }
        const amount = Math.min(remaining, MAX_BATCH_MS - batch.duration_ms);
        batch.duration_ms += amount;
        remaining -= amount;
    }
}

async function flushPending(force = false): Promise<void> {
    if (flushing) return;
    if (Date.now() < nextRetryAt) return;
    const batch = pendingBatches[0];
    if (!batch || (!force && batch.duration_ms < FLUSH_INTERVAL_MS)) return;

    pendingBatches.shift();
    flushing = true;
    const baseUrl = vscode.workspace
        .getConfiguration('dronaActivityTracker')
        .get<string>('serverUrl', DEFAULT_SERVER_URL)
        .replace(/\/+$/, '');

    try {
        const response = await fetch(`${baseUrl}/api/coding-activity`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(batch),
            signal: AbortSignal.timeout(5000),
        });
        if (!response.ok) throw new Error(`Drona server returned ${response.status}`);
        serverUnavailable = false;
        nextRetryAt = 0;
        hasLoggedServerError = false;
        await extensionContext.globalState.update('pendingBatches', pendingBatches);
    } catch (error) {
        pendingBatches.unshift(batch);
        serverUnavailable = true;
        nextRetryAt = Date.now() + 15_000;
        await extensionContext.globalState.update('pendingBatches', pendingBatches);
        if (!hasLoggedServerError) {
            console.error('[Drona Activity Tracker] Could not sync coding activity:', error);
            hasLoggedServerError = true;
        }
    } finally {
        flushing = false;
        updateStatus();
    }
}

export function activate(context: vscode.ExtensionContext): void {
    extensionContext = context;
    pendingBatches = context.globalState.get<ActivityBatch[]>('pendingBatches', []);
    trackingEnabled = context.globalState.get<boolean>('trackingEnabled', true);
    console.log('Drona Activity Tracker is active. It records project and language only.');

    statusItem = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Left, 10);
    statusItem.command = 'drona-activity-tracker.toggleTracking';
    context.subscriptions.push(statusItem);
    statusItem.show();

    const toggleCommand = vscode.commands.registerCommand(
        'drona-activity-tracker.toggleTracking',
        async () => {
            if (trackingEnabled) await flushPending(true);
            trackingEnabled = !trackingEnabled;
            await context.globalState.update('trackingEnabled', trackingEnabled);
            lastActivityAt = 0;
            updateStatus();
            void vscode.window.showInformationMessage(
                trackingEnabled ? 'Drona automatic tracking resumed.' : 'Drona automatic tracking paused.'
            );
        },
    );
    context.subscriptions.push(toggleCommand);

    const editListener = vscode.workspace.onDidChangeTextDocument(event => {
        if (!trackingEnabled || event.contentChanges.length === 0) return;
        const document = event.document;
        if (document.uri.scheme !== 'file' || document.isUntitled) return;
        if (['plaintext', 'markdown', 'log'].includes(document.languageId)) return;

        const folder = vscode.workspace.getWorkspaceFolder(document.uri);
        if (!folder) return;

        activeProject = folder.name.slice(0, 120);
        activeLanguage = document.languageId.slice(0, 50);
        lastActivityAt = Date.now();
        serverUnavailable = false;
        updateStatus();
    });
    context.subscriptions.push(editListener);

    const timer = setInterval(() => {
        const now = Date.now();
        if (trackingEnabled && lastActivityAt > 0) {
            const activeFrom = Math.max(lastTickAt, lastActivityAt);
            const activeUntil = Math.min(now, lastActivityAt + getIdleTimeout());
            if (activeUntil > activeFrom) queueActivity(activeUntil - activeFrom, now);
        }
        if (pendingBatches.length) void flushPending();
        lastTickAt = now;
        updateStatus();
    }, 1000);
    context.subscriptions.push({ dispose: () => clearInterval(timer) });
    updateStatus();
}

export async function deactivate(): Promise<void> {
    while (pendingBatches.length > 0 && !serverUnavailable) {
        await flushPending(true);
        if (flushing) break;
    }
}
