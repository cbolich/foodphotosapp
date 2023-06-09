#only serve 1 thing at a time to automatic1111
#not sure if this goes here or inside nginx

#need to tie this to a status pull from automatic1111
#this is just example code


import threading
import time
import queue
import asyncio
import requests

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

async def worker(input_queue, output_queue, url, payload):
    while True:
        request = await input_queue.get()
        if request == "STOP":
            break
        result = requests.post(url, json=payload, timeout=1000)
        await output_queue.put(result.json())

async def queuing_function(request, url, payload):
    input_queue = asyncio.Queue()
    output_queue = asyncio.Queue()

    # Start the worker task
    worker_task = asyncio.create_task(worker(input_queue, output_queue, url, payload))

    # Enqueue the requests
    await input_queue.put(request)

    # Add a sentinel to stop the worker task
    await input_queue.put("STOP")

    # Wait for the worker to finish processing all requests
    await worker_task

    # Retrieve the results
    results = []
    while not output_queue.empty():
        results.append(await output_queue.get())

    return results
