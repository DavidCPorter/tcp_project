---
title: Homework 6
description: Reliable Communication II
due: Friday, May 04 
assigned: Tuesday, April 25
additional_css: [syntax.css]
---


## {{ page.title }}: {{ page.description }}

--------

##### **This assignment is an extra credit homework and the scores will be added towards your overall homework grade.**

##### **This assignment is due at 11:59pm on May 4, 2018.**

##### **You can download the homework zip archive [here]({{ site.url }}{{ site.baseurl }}/downloads/hw6.zip).**

---------

# Homework 6: Reliable Communication II

In this homework, you will improve upon the stop and wait implementation of
homework 5.  Please see the description of Homework 5 for the basics, and the
April 17 lecture on YouTube for advice on how to get started. Everything is
the same about this assignment except for the file sizes, buffer sizes, and
throughput cutoffs. All of the files have been kept named as "homework 5" for
ease of portability. We have the skeleton code for HW5 in this archive. You are 
welcome to use your implementation of the stop and wait `hw5.py`.


### Writing Your Solution

This repo contains several tools that will help you simulate and test your
solution.  **You should not make changes to any file other than `hw5.py`.**
All other files contain code used to either simulate the unreliable connection,
or code to help you test your your solution.

Your solution / `hw5.py` file will be tested against stock versions of all the
other files in the repo, so any changes you make will not be present at
grading time.

Your solution must be contained in the `send` and `recv` functions in `hw5.py`.
You should not change the signatures of these functions, only their bodies.
These functions will be called by the grading script, with parameters
controlled by the grading script.  Your solution must be general, and should
work for any file.

Your task is to modify the bodies of these functions so that they communicate
using a protocol that ensures that the data sent by the `send` function
can be reliably and quickly reconstructed by the `recv` function.  You should
do so through a combination of setting timeouts on socket reads (e.x.
`socket.timeout(float)`) and developing a system through which each side can
acknowledge if / when they receive a packet.


### Testing Your Solution

You can use the provided `tester.py` script when testing your solution.  This
script uses the `receiver.py`, `sender.py`, and `server.py` scripts to
simulate an unreliable connection, and to test your solution.

The `tester.py` script contains many parameters you can use to test your
solution under different conditions, and to receive different amounts
of debugging information to better understand the network.  These
parameters and options can be viewed by calling `tester.py --help`, and are
also reproduced below.


    usage: tester.py [-h] [-p PORT] [-l LOSS] [-d DELAY] [-b BUFFER] -f FILE
                    [-r RECEIVE] [-s] [-v]

    Utility script for testing HW5 solutions under user set conditions.

    optional arguments:
    -h, --help            show this help message and exit
    -p PORT, --port PORT  The port to simulate the lossy wire on (defaults to
                            9999).
    -l LOSS, --loss LOSS  The percentage of packets to drop.
    -d DELAY, --delay DELAY
                            The number of seconds, as a float, to wait before
                            forwarding a packet on.
    -b BUFFER, --buffer BUFFER
                            The size of the buffer to simulate.
    -f FILE, --file FILE  The file to send over the wire.
    -r RECEIVE, --receive RECEIVE
                            The path to write the received file to. If not
                            provided, the results will be written to a temp file.
    -s, --summary         Print a one line summary of whether the transaction
                            was successful, instead of a more verbose description
                            of the result.
    -v, --verbose         Enable extra verbose mode.


For example, to see how your solution performs when transmitting a text file,
with a 5% loss rate, and with a latency of 100ms, you could use the following:
`python3 tester.py --file test_data.txt --loss .05 --delay 0.1`.


### Hints and Suggestions

 * Use the included `--verbose` option to include very detailed information
   about what your code is sending over the network, and how the network
   is handling that data.

 * Use the included `--receive` option to see the results of your file transfer.
   By default, the testing script will store the results of your code to a
   temporary location.  This option may be useful if you're not sure how or
   why the received file does not match the sent file.

 * Make sure you try your solution under many different loss ratios and
   latencies by changing the parameters in the `tester.py` script. In the next
  section, we have also provided you with the test cases and latencies for 
  evaluating the performance of your implementation.

 * Keep your packets smaller than or equal to `homework5.MAX_PACKET` (1400
   bytes).


### Grading

You solution will be graded by using it to transfer six different files,
each under different simulated test conditions.  For each test case, there is a
minimum throughput requirement and a timeout for your program to exit.
The timeout is set as 50% more than the corresponding required throughput.

The table below provides the test case parameters for `tester.py` along with 
the upper bounds of the fast and slow transmissions.

<table class="table table-striped">
<thead>
<tr>
<th>Case #</th>
<th>File Size</th>
<th>Loss</th>
<th>Delay</th>
<th>Buffer</th>
<th>Fast</th>
<th>Slow</th>
</tr>
</thead>

<tbody>

<tr>
<td>1</td>
<td>10KB</td>
<td>0</td>
<td>0.5</td>
<td>10</td>
<td>10.5</td>
<td>14</td>
</tr>

<tr>
<td>2</td>
<td>100KB</td>
<td>0</td>
<td>0.1</td>
<td>20</td>
<td>7.5</td>
<td>10</td>
</tr>

<tr>
<td>3</td>
<td>2MB</td>
<td>0</td>
<td>0.01</td>
<td>30</td>
<td>9</td>
<td>12</td>
</tr>

<tr>
<td>4</td>
<td>30KB</td>
<td>0.1</td>
<td>0.1</td>
<td>40</td>
<td>9</td>
<td>12</td>
</tr>

<tr>
<td>5</td>
<td>4MB</td>
<td>0.1</td>
<td>0.01</td>
<td>50</td>
<td>48</td>
<td>64</td>
</tr>

<tr>
<td>6</td>
<td>5MB</td>
<td>0</td>
<td>0.01</td>
<td>60</td>
<td>18</td>
<td>24</td>
</tr>

</tbody>
</table>



Each test case will be scored accordingly:

<table class="table table-striped">
<thead>
<tr>
<th>Case</th>
<th> Points Earned</th>
</tr>
</thead>
<tbody>
<tr>
<td>File is not transmitted correctly</td>
<td>0</td>
</tr>
<tr>
<td> Transmission takes longer than the max time</td>
<td>0</td>
</tr>
<tr>
<td>Successful transmission, but low throughput</td>
<td>1</td>
</tr>
<tr>
<td>Successful transmission, fast throughput </td>
<td>2</td>
</tr>
</tbody>
</table>


If your program exits normally before the timeout, but the content of the
received file is invalid, then **zero points** are awarded.

If your program doesn’t exit before the timeout, it will be terminated
before completion, resulting in incorrect file content, and so **0 points**.

If the program exits normally before the timeout and the received file’s content
is valid *but* the throughput obtained is lower than the required minimum
throughput then you receive **1 point**.

If your program correctly transmits the file below the timeout, and with the
required throughput, it will receive **2 points**.

Code that earns at least 5 of the above points, and which is both "PEP 8" and
"pylint" compatible will earn an additional **1 point**.

There are 13 points possible on this assignment.  Your solution will be graded
out of 12 possible points.




## Submission Instructions
You will be making the submission for this homework through the OK client. 
When you first download the homework, make sure you authenticate using 
`python3 ok --authenticate`. To save your work, feel free to create as many backups as you like.

You will be making changes to `hw5.py` and that is the only file that will be 
submitted for grading by the ok client:

To submit your work, run `python3 ok --submit`. Like previously, you are allowed 
to make multiple submissions. The most recent submission before the deadline will be graded.

## Due Date and Logistics

* This assignment is due at the at 11:59 pm on Friday, May 04, 2018.

* If you have any questions please use the [Piazza](https://piazza.com/class/j9oqs0y7d01k0) discussion forum.