
const plan = document.getElementById("plan-form")
const taskInput = document.getElementById("plan-task-input")
const taskList = document.getElementById("plan-task-list")
const completed = document.getElementById("plan-completion")
const progress = document.getElementById("plan-progress-fill")
const progressBar = document.getElementById("plan-progress-track")

const now = new Date();
const today_date = `${now.getFullYear()}-${now.getMonth() + 1}-${now.getDate()}`
const focusPlanStorageKey = `drona-focus-plan for ${today_date}`;
console.log(focusPlanStorageKey)
let tasks = [];

try {
    const savedTasks = localStorage.getItem(focusPlanStorageKey);
    tasks = savedTasks ? JSON.parse(savedTasks) : [];
    if (!Array.isArray(tasks)) tasks = [];
} catch {
    tasks = [];
}
function saveTasks() {
    localStorage.setItem(focusPlanStorageKey, JSON.stringify(tasks));
}
function render(){
    taskList.replaceChildren()
    tasks.forEach((task,index) => {
        const t = document.createElement("li");
        const t_check = document.createElement('input');
        const t_button = document.createElement('button');

        t.textContent = task.text;
        t_check.type = "checkbox"
        t_check.checked = task.done
        t_button.textContent = "x"
        t_button.type = "button";
       
        t.append(t_check)
        t.append(t_button)
        taskList.append(t)
        t_check.addEventListener("change",() => {
            tasks[index].done = t_check.checked;
            saveTasks()
            render()})
        t_button.addEventListener('click',() => {
            tasks.splice(index,1)
            saveTasks()
            render()
        })
    }
    )
    let total = tasks.length
    let done = tasks.filter(task => task.done).length;
    completed.textContent = `you have completed ${done} tasks` 
    
    const percent = total ? (done / total) * 100 : 0;
    progress.style.width = percent + "%"
}

render()

plan.addEventListener("submit",event=>{
    console.log("sf")
    event.preventDefault()
    const text = taskInput.value.trim()
    console.log(text)
    if(!text){
        return
    }
    tasks.push({text,done:false})
    saveTasks()
    render()
    taskInput.value = "";
})


console.log(tasks)
