#Simple Interpreter

Interpreter for the FLAIL language for microdrones. <br>
Version 1.2. <br><br>

Currently accepts the following commands: <br>
Ascend, <br>
Forward, <br>
Backwards, <br>
Left, <br>
Right, <br>
Roll Left, <br>
Roll Right, <br>
Descend, <br>
Repeat <iterations> { <Flail instructions> }, <br>
Wait (seconds), <br>
WaitMili (miliseconds) <br><br>

Bugs: <br>
Parameter is not set before the conflicting instruction check is performed in interpretToken method. 
<br>
Set a default mode for the program if an invalid mode is given. Or exit the program.<br>





