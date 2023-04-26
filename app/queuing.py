#only serve 1 thing at a time to automatic1111
#not sure if this goes here or inside nginx

#need to tie this to a status pull from automatic1111
#this is just example code


import threading
import time
import queue
import asyncio

# def function_to_execute():
#     # Simulating a function that takes some time to execute
#     time.sleep(2)
#     return "Function completed."

queue_status = {
    "queue_size": 0,
    "avg_event_process_time": 0,
    "avg_event_concurrent_process_time": 0,
}

def get_queue_status(user_id=None):
    queue_size = queue_status["queue_size"]
    avg_event_process_time = queue_status["avg_event_process_time"]

    rank = 0
    rank_eta = 0

    # Example logic to calculate rank and rank ETA based on user_id
    if user_id:
        rank = user_id % (queue_size + 1)
        rank_eta = rank * avg_event_process_time

    queue_eta = queue_size * avg_event_process_time

    status = {
        "queue_size": queue_size,
        "avg_event_process_time": avg_event_process_time,
        "avg_event_concurrent_process_time": queue_status["avg_event_concurrent_process_time"],
        "rank": rank,
        "rank_eta": rank_eta,
        "queue_eta": queue_eta,
    }
    return status

async def worker(input_queue, output_queue):
    while True:
        request = await input_queue.get()
        if request is None:
            break
        result = function_to_execute()
        await output_queue.put(result)
        input_queue.task_done()

async def queuing_function(requests):
    input_queue = asyncio.Queue()
    output_queue = asyncio.Queue()

    # Start the worker task
    worker_task = asyncio.create_task(worker(input_queue, output_queue))

    # Enqueue the requests
    for request in requests:
        await input_queue.put(request)

    # Add a sentinel to stop the worker task
    await input_queue.put(None)

    # Wait for the worker to finish processing all requests
    await input_queue.join()

    # Retrieve the results
    results = []
    while not output_queue.empty():
        results.append(await output_queue.get())

    return results

# Test the queuing function
# requests = ["Request 1", "Request 2", "Request 3"]
# results = queuing_function(requests)

# for idx, result in enumerate(results):
#     print(f"Result for {requests[idx]}: {result}")
