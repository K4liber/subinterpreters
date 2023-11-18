window.worker = void 0, window.so = void 0;
const n = 42;

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
const noJobs = 40;
const workerIdToTasksDone = new Map();

const startWorkers = () => {
    workers.forEach((worker, workerId) => {
        workerIdToTasksDone.set(workerId, 0)
        worker.port.onmessage = (e) => {
            workerIdToTasksDone.set(workerId, workerIdToTasksDone.get(workerId) + 1)
            console.log("Worker " + workerId + ", result = " + e.data.result);
            updateWorkerProgress(workerId)
        };
        updateWorkerProgress(workerId)
        worker.port.start();
        worker.port.postMessage({n: n});
        console.log('Started worker ' + workerId)
    })    
};

const updateWorkerProgress = (workerId) => {
    let percentageProgress = workerIdToTasksDone.get(workerId)/noJobs
    let workerElementId = 'worker-progress-' + workerId
    document.getElementById(workerElementId).innerHTML = percentageProgress
};

const getWorkersProgressHTML = () => {
    var workersProgressHTML = "";
    workers.forEach((_, workerId) => {
        workersProgressHTML += '<div>Worker ' + workerId + ':</div>' + '<div id="worker-progress-' + workerId + '"></div>'
    })
    return workersProgressHTML
}

document.getElementById('start-buttom').onclick = (e) => {
    startWorkers()
};
document.getElementById('workers-progress').innerHTML = getWorkersProgressHTML()
