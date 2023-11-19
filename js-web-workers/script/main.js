window.worker = void 0, window.so = void 0;
const n = 38;

const workers = [
    new SharedWorker("script/fibonacci.js?" + (Date.now())),
    new SharedWorker("script/fibonacci.js?" + (Date.now())),
    new SharedWorker("script/fibonacci.js?" + (Date.now())),
    new SharedWorker("script/fibonacci.js?" + (Date.now())),
    new SharedWorker("script/fibonacci.js?" + (Date.now())),
    new SharedWorker("script/fibonacci.js?" + (Date.now())),
    new SharedWorker("script/fibonacci.js?" + (Date.now())),
    new SharedWorker("script/fibonacci.js?" + (Date.now()))
]
const noWorkers = workers.length;
const noJobs = 40;
const workerIdToTasksDone = new Map();

const startWorkers = () => {
    document.getElementById('start-buttom').setAttribute('disabled', 'True')
    workers.forEach((worker, workerId) => {
        workerIdToTasksDone.set(workerId, 0)
        worker.port.onmessage = (e) => {
            workerIdToTasksDone.set(workerId, workerIdToTasksDone.get(workerId) + 1)
            console.log("Worker " + workerId + ", result = " + e.data.result);
            updateWorkerProgress(workerId)
        };
        updateWorkerProgress(workerId)
        worker.port.start();
        console.log('Started worker ' + workerId)
    })
    // Submit jobs
    for (const jobIndex of Array(noJobs).keys()) {
        let workerId = jobIndex % noWorkers
        let worker = workers[workerId]
        worker.port.postMessage({n: n});
        console.log('Job ' + jobIndex + ' submitted')
    }
};

const updateWorkerProgress = (workerId) => {
    let percentageProgress = 100.0 * workerIdToTasksDone.get(workerId)/noJobs + '%'
    let workerElementId = 'worker-progress-' + workerId
    document.getElementById(workerElementId).style.width = percentageProgress
    // Update overall progress
    var overallCompleted = 0;

    workers.forEach((_, workerId) => {
        overallCompleted += workerIdToTasksDone.get(workerId)
    })

    document.getElementById('overall-progress').style.width = 100.0 * overallCompleted/noJobs + '%'

    if (overallCompleted == noJobs) {
        console.log('Successfull finish')
        document.getElementById('start-buttom').removeAttribute('disabled')
    }
};

const getWorkersProgressHTML = () => {
    var workersProgressHTML = '<div class="worker-div"><div class="worker-label">Overall:</div><div class="worker-progress"><div class="worker-progress-internal" id="overall-progress"></div></div></div>';
    workers.forEach((_, workerId) => {
        workersProgressHTML += '<div class="worker-div"><div class="worker-label">Worker ' + workerId + ':</div><div class="worker-progress"><div class="worker-progress-internal" id="worker-progress-' + workerId + '"></div></div></div>'
    })
    return workersProgressHTML
}

document.getElementById('start-buttom').onclick = (e) => {
    startWorkers()
};
document.getElementById('workers-progress').innerHTML = getWorkersProgressHTML()
