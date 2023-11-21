using System;
using System.Collections.Concurrent;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;
using System.Threading;
using System.Threading.Tasks;

class Program
{
    static async Task Main(string[] args)
    {
        var noJobs = 40;
        var n = 35;
        int[] data = Enumerable.Repeat(n, noJobs).ToArray();
        var workers = Worker(data, 8);
        var tasks = new List<Task>();

        Stopwatch stopwatch = Stopwatch.StartNew();

        // Create a BlockingCollection to store the results
        BlockingCollection<(int workerId, long result)> results = new BlockingCollection<(int, long)>();

        foreach (var (workerTasks, workerId) in workers.Select((v, i) => (v, i)))
        {
            tasks.Add(Task.Run(async () =>
            {
                foreach (var item in workerTasks)
                {
                    long result = Fibonacci(item);
                    // Store the result with the worker identifier in the thread-safe collection
                    results.Add((workerId, result));
                    // Simulate other work by Worker
                    await Task.Delay(10);
                }
            }));
        }

        var collectingTask = Task.Run(() =>
        {
            foreach (var (workerId, result) in results.GetConsumingEnumerable())
            {
                Console.WriteLine($"Worker {workerId}, result = {result}");
            }
        });

        // Wait for all tasks to complete
        await Task.WhenAll(tasks);
        // Mark that no more items will be added
        results.CompleteAdding();
        // Also wait for the collecting task
        await collectingTask;

        stopwatch.Stop();
        Console.WriteLine($"Time elapsed: {stopwatch.Elapsed}");
    }

    static long Fibonacci(int n)
    {
        if (n <= 1) return n;

        return Fibonacci(n - 1) + Fibonacci(n - 2);
    }

    static IEnumerable<IEnumerable<T>> Worker<T>(IEnumerable<T> source, int noWorkers)
    {
        int i = 0;
        return source.GroupBy(x => i++ % noWorkers);
    }
}