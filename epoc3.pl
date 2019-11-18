% initMyData(+NBoxesToPick, -ProgramDataInitial).
% Here, you have to choose and initialise  a structure ProgramData
% Intuition:
%   ProgramData represents the "agenda" where the robotul keeps track of
%     - where it is,
%     - what is his state (does it hold a box or not), and
%     - what it has to do
%

% initMyData(+NBoxesToPick, (CurrentPosition,NBoxesToPick,LastVisitedPosition,HasBox)).
% ...

% perform(+ProgramData, +ContainsBox, -Action, -ProgramDataUpdated)
% ...



/*
 * Possible Actions
 */

done.
pickBox.
deliverBox.
move(north).
move(east).
move(south).
move(west).
moveWithBox(north).
moveWithBox(east).
moveWithBox(south).
moveWithBox(west).

/*
 * Defined Rules
 * array as follow - [x, y, nrBoxLeft, holdsBox, lastX, lastY, GolastLocation]
 * lastX and lastY is the bosition from where the robot has picked the last box
 * After he beliveres the box he will need to get back to the last place
 * GolastLocation flag is for the case in which the robot had delivered the box,
 * and he needs to go back to the previous location
 */

has_no_box(ProgramData):- ProgramData = [_, _, _, false, _, _, _].
has_box(ProgramData):- ProgramData = [_, _, _, true, _, _, _].

go_last_location(ProgramData):- ProgramData = [_, _, _, _, _, _, true].

is_finished(ProgramData):- ProgramData = [_, _, N, _, _, _, _], N = 0.
in_origin(ProgramData):- ProgramData = [X, Y, _, _, _, _, _], X = 0, Y = 0.

/*
 * update the ProgramData for the case we found a box
 * we will need to set the has_box parameter for true 
 * and also we will need to save the possition where we found the box
 * such that after we deliver it we can get back to the same possition and continue our search
 * we will also need to set the flag for go_last_location(has to come back after box deliver) to true
 */

find_box_status_update(ProgramData, ProgramDataUpdated):-
    ProgramData = [T1, T2, T3, false, _, _, _], ProgramDataUpdated = [T1, T2, T3, true, T1, T2, true]
    .

/*
 * update the ProgramData for the case when the robot delivers the 
 * box to the origin point
 * we will need to decrement the number of needed boxes and set the flag for has_box to false
 */

delivered_box_status_update(ProgramData, ProgramDataUpdated):-
    ProgramData = [T1, T2, T3, _, T4, T5, T6], NT3 is T3 - 1, ProgramDataUpdated = [T1, T2, NT3, false, T4, T5, T6]
    .

/*
 * after the robot had picked a box we will need to
 * deliver that box to the origin
 */

update_move_holding_box(ProgramData, ProgramDataUpdated, Action):-
    ProgramData = [X, Y, BoxLeft, HasBox, XLast, YLast, GoLastLocation] , X < 0 -> (X_New is X + 1, ProgramDataUpdated = [X_New, Y, BoxLeft, HasBox, XLast, YLast, GoLastLocation], Action = moveWithBox(east));
    ProgramData = [X, Y, BoxLeft, HasBox, XLast, YLast, GoLastLocation], X > 0 -> (X_New is X - 1, ProgramDataUpdated = [X_New, Y, BoxLeft, HasBox, XLast, YLast, GoLastLocation], Action = moveWithBox(west));
    ProgramData = [X, Y, BoxLeft, HasBox, XLast, YLast, GoLastLocation], Y < 0 -> (Y_New is Y + 1, ProgramDataUpdated = [X, Y_New, BoxLeft, HasBox, XLast, YLast, GoLastLocation], Action = moveWithBox(north));
    ProgramData = [X, Y, BoxLeft, HasBox, XLast, YLast, GoLastLocation], Y > 0 -> (Y_New is Y - 1, ProgramDataUpdated = [X, Y_New, BoxLeft, HasBox, XLast, YLast, GoLastLocation], Action = moveWithBox(south))
    .

/*
 * this function will get the robot to the last possition 
 * where it found the last box, after the box was delivered to origin
 *
 * First we have to check if the position of the place from where
 * the robot had picked the box was reached, and if so set the go_last_location to false
 * otherwise move to the last place
 */

update_to_last_location(ProgramData, ProgramDataUpdated, Action):-
    ProgramData = [X, Y, BoxLeft, HasBox, XLast, YLast, _], X = XLast, Y = YLast -> (ProgramDataNew = [X, Y, BoxLeft, HasBox, XLast, YLast, false], update_move(ProgramDataNew, ProgramDataUpdated, Action));
    ProgramData = [X, Y, BoxLeft, HasBox, XLast, YLast, GoLastLocation], X < XLast -> (X_New is X + 1, ProgramDataUpdated = [X_New, Y, BoxLeft, HasBox, XLast, YLast, GoLastLocation], Action = move(east));
    ProgramData = [X, Y, BoxLeft, HasBox, XLast, YLast, GoLastLocation], X > XLast -> (X_New is X - 1, ProgramDataUpdated = [X_New, Y, BoxLeft, HasBox, XLast, YLast, GoLastLocation], Action = move(west));
    ProgramData = [X, Y, BoxLeft, HasBox, XLast, YLast, GoLastLocation], Y < YLast -> (Y_New is Y + 1, ProgramDataUpdated = [X, Y_New, BoxLeft, HasBox, XLast, YLast, GoLastLocation], Action = move(north));
    ProgramData = [X, Y, BoxLeft, HasBox, XLast, YLast, GoLastLocation], Y > YLast -> (Y_New is Y - 1, ProgramDataUpdated = [X, Y_New, BoxLeft, HasBox, XLast, YLast, GoLastLocation], Action = move(south))
    .

/*
 * I chose to move the robot in a spiral shape because
 * I found it the best approache when we have a infinite space
 *
 * If we are in origin we will make the first move to the right and than continue in spiral
 * 
 * I will have to check if the robot is in one of the 4 possible quadrants
 * 
 * Special case for the right-bottom one --- if we hit the right corner we will need to go one 
 * step to the right (to not remain in the same circle) to be able to continue spiraling
 */

update_move(ProgramData, ProgramDataUpdated, Action):-
    ProgramData = [X, Y, BoxLeft, HasBox, XLast, YLast, GoLastLocation], X = 0, Y = 0 -> (X_New is X + 1, ProgramDataUpdated = [X_New, Y, BoxLeft, HasBox, XLast, YLast, GoLastLocation], Action = move(east));
    /* 1 - quadrant */
    ProgramData = [X, Y, BoxLeft, HasBox, XLast, YLast, GoLastLocation], X > 0, Y >= 0, Max is max(X,Y), X = Max, Y\= Max -> (Y_New is Y + 1, ProgramDataUpdated = [X, Y_New, BoxLeft, HasBox, XLast, YLast, GoLastLocation], Action = move(north));
    ProgramData = [X, Y, BoxLeft, HasBox, XLast, YLast, GoLastLocation], X > 0, Y > 0, Max is max(X,Y), X = Max, Y = Max -> (X_New is X - 1, ProgramDataUpdated = [X_New, Y, BoxLeft, HasBox, XLast, YLast, GoLastLocation], Action = move(west));
    ProgramData = [X, Y, BoxLeft, HasBox, XLast, YLast, GoLastLocation], X > 0, Y > 0, Max is max(X,Y), X \= Max, Y = Max -> (X_New is X - 1, ProgramDataUpdated = [X_New, Y, BoxLeft, HasBox, XLast, YLast, GoLastLocation], Action = move(west));
    /* 2 - quadrant */
    ProgramData = [X, Y, BoxLeft, HasBox, XLast, YLast, GoLastLocation], X < 0, Y > 0, X_abs is abs(X), Max is max(X_abs,Y), X_abs = Max, Y = Max -> (Y_New is Y - 1, ProgramDataUpdated = [X, Y_New, BoxLeft, HasBox, XLast, YLast, GoLastLocation], Action = move(south));
    ProgramData = [X, Y, BoxLeft, HasBox, XLast, YLast, GoLastLocation], X < 0, Y > 0, X_abs is abs(X), Max is max(X_abs,Y), X_abs = Max, Y \= Max -> (Y_New is Y - 1, ProgramDataUpdated = [X, Y_New, BoxLeft, HasBox, XLast, YLast, GoLastLocation], Action = move(south));
    ProgramData = [X, Y, BoxLeft, HasBox, XLast, YLast, GoLastLocation], X =< 0, Y > 0, X_abs is abs(X), Max is max(X_abs,Y), X_abs \= Max, Y = Max -> (X_New is X - 1, ProgramDataUpdated =[X_New, Y, BoxLeft, HasBox, XLast, YLast, GoLastLocation], Action = move(west));
    /* 3 - quadrant */
    ProgramData = [X, Y, BoxLeft, HasBox, XLast, YLast, GoLastLocation], X < 0, Y < 0, X_abs is abs(X), Y_abs is abs(Y), Max is max(X_abs,Y_abs), X_abs = Max, Y_abs = Max -> (X_New is X + 1, ProgramDataUpdated =[X_New, Y, BoxLeft, HasBox, XLast, YLast, GoLastLocation], Action = move(east));
    ProgramData = [X, Y, BoxLeft, HasBox, XLast, YLast, GoLastLocation], X < 0, Y < 0, X_abs is abs(X), Y_abs is abs(Y), Max is max(X_abs,Y_abs), X_abs \= Max, Y_abs = Max -> (X_New is X + 1, ProgramDataUpdated =[X_New, Y, BoxLeft, HasBox, XLast, YLast, GoLastLocation], Action = move(east));
    ProgramData = [X, Y, BoxLeft, HasBox, XLast, YLast, GoLastLocation], X < 0, Y =< 0, X_abs is abs(X), Y_abs is abs(Y), Max is max(X_abs,Y_abs), X_abs = Max, Y_abs \= Max -> (Y_New is Y - 1, ProgramDataUpdated =[X, Y_New, BoxLeft, HasBox, XLast, YLast, GoLastLocation], Action = move(south));
    /* 4 - quadrant */
    ProgramData = [X, Y, BoxLeft, HasBox, XLast, YLast, GoLastLocation], X > 0, Y < 0, X_abs is abs(X), Y_abs is abs(Y), Max is max(X_abs,Y_abs), X_abs = Max, Y_abs = Max -> (X_New is X + 1, ProgramDataUpdated =[X_New, Y, BoxLeft, HasBox, XLast, YLast, GoLastLocation], Action = move(east));
    ProgramData = [X, Y, BoxLeft, HasBox, XLast, YLast, GoLastLocation], X > 0, Y < 0, X_abs is abs(X), Y_abs is abs(Y), Max is max(X_abs,Y_abs), X_abs = Max, Y_abs \= Max -> (Y_New is Y + 1, ProgramDataUpdated =[X, Y_New, BoxLeft, HasBox, XLast, YLast, GoLastLocation], Action = move(north));
    ProgramData = [X, Y, BoxLeft, HasBox, XLast, YLast, GoLastLocation], X >= 0, Y < 0, X_abs is abs(X), Y_abs is abs(Y), Max is max(X_abs,Y_abs), X_abs \= Max, Y_abs = Max -> (X_New is X + 1, ProgramDataUpdated =[X_New, Y, BoxLeft, HasBox, XLast, YLast, GoLastLocation], Action = move(east))
    .

perform(ProgramData, ContainsBox, Action, ProgramDataUpdated):-
    is_finished(ProgramData) -> (ProgramDataUpdated = ProgramData, Action = done);
    ContainsBox = true, has_no_box(ProgramData) -> ( find_box_status_update(ProgramData, ProgramDataUpdated), Action = pickBox ); 
    in_origin(ProgramData), has_box(ProgramData) -> ( delivered_box_status_update(ProgramData,ProgramDataUpdated), Action = deliverBox ); 
    has_box(ProgramData) -> ( update_move_holding_box(ProgramData, ProgramDataUpdated, Action));
    has_no_box(ProgramData), go_last_location(ProgramData) -> ( update_to_last_location(ProgramData, ProgramDataUpdated, Action) );
    has_no_box(ProgramData) -> (update_move(ProgramData, ProgramDataUpdated, Action))
    .

initMyData(N,ProgramData):-
        ProgramData = [0,0,N,false,0,0,false].


