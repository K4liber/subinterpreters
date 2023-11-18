const fibonacci = n => {
    return n < 2 ? n : fibonacci(n-1) + fibonacci(n-2);
};

self.onconnect = function(e) {
    console.log('Connected: ' + e)
    var port = e.ports[0];

    port.onmessage = (e) => {
        n = e.data.n;
        console.log('Worker received a task');
        port.postMessage({
            result: fibonacci(n)
        });
    };

}
