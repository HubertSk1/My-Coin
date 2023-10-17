import time
import asyncio

async def task1():
    print("task 1 started")
    await  asyncio.sleep(2)
    print("task 1 finished")

async def task2():
    print("task 2 started")
    await asyncio.sleep(2)
    print("task 2 finished")

loop = asyncio.get_event_loop()
tasks = [
    loop.create_task(task1()),
    loop.create_task(task2())]
 
loop.run_until_complete(asyncio.wait(tasks))
loop.close()
