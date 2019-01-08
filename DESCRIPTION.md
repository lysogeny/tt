Text-file based time-tracking
=============================

This file describes how to track your time using simple text files similar to
the excellent todo-txt Todo system.

We consider a single table of events.
Each event in this table is a start of a new activity. When a new activity
starts, the previous activity ends.

For instance, our activities might look like:

- Food
- Free
- Work

Starting a new activity 'work' while 'free' is going on will end the free
segment and start the 'work' segment. Analysing this data is somewhat similar
to some path-segmentations done in movement ecology.

The categories above are not the most descriptive. Ideally, 'work' could be
further subdivided into separate projects, like 'writing', 'project 20',
'meeting' or something.

To do this we might make our category more descriptive by introducing hierarchy
like this:

- Work
- Work:Writing
- Work:Writing:Introduction

Separating by colons might give us a hierarchy.

And thus, a row in our table might look like:

| Timestamp (UTC)      | Activity     |
|----------------------|--------------|
| 2018-08-08T17:00:00Z | Work:Writing |

Several things might be a good idea for the timestamp:

- Either a ISO 8601 formatted character string, which is easily generated using
  tools such as `date` (eg. `date -u '+%FT%TZ'`)
- The canonical way of storing data on a UNIX system, the UNIX timestamp:
  Seconds since 1970.

Unix timestamps are probably a bit smaller, and more convenient for most
programming needs. However they are not as easily understood by the user, which
runs counter to the `todo.txt` philosophy.
For the sake of user understandability and usability using ISO 8601 date time
is probably the best solution. 
For the ease of programming, the UNIX timestamps are better.

Which format to choose is not quite clear. Fixing down on the user's time zone
_will_ cause problems when the user travels across time zones. Using UNIX
timestamps or UTC will avoid the travel problem, but cause other problems: The
user might not as readily understand what is written in the file. 

Unlike `todo.txt`, there is not as much purpose to having the file be
user-editable. And for those cases that the user might want to edit something
we could provide a interface for doing that.

Realistically these two fields are all that is needed to make a time-tracking
software.
Ancillary data might be provided, like a `location` or something, that will
allow statistical analyses based on work locations or other things. How this
should be implemented is not quite clear to me. It is easy to get geodata on
phones, but on computers that is not as trivial. Perhaps identification over
the network properties (IP ranges, gateway, ...) might be a solution.
Alternatively the user might want to provide this data themselves. This would
however place a bit of a burden on the user.

Another field that might be useful is a `hostname` field that allows tracking
from which machine created the entry.


Analysis
--------

This type of data can be transformed into segment data easily.
For instance the following R function

    segmentify <- function(d) {
      # create a lagged combined data frame with starts and ends for each bit.
      if (nrow(d) > 1) {
        start_d <- d[1:nrow(d)-1, ]
        end_d <- d[2:nrow(d), ]
      } else {
        start_d <- end_d <- d[F, ]
      }
      names(start_d) <- paste('start', names(d), sep='_')
      names(end_d) <- paste('end', names(d), sep='_')
      return(cbind(start_d, end_d))
    }

Will take the any table and create a lagged copy in the columns. For example:

| timestamp            | activity          |
|----------------------|-------------------|
| 2018-08-08T17:00:00Z | Work:Writing      |
| 2018-08-08T18:00:00Z | Work:Introduction |
| 2018-08-08T19:00:00Z | Free              |

becomes

| start_timestamp      | end_timestamp        | start_activity    | end_activity      |
|----------------------|----------------------|-------------------|-------------------|
| 2018-08-08T17:00:00Z | 2018-08-08T18:00:00Z | Work:Writing      | Work:Introduction |
| 2018-08-08T18:00:00Z | 2018-08-08T19:00:00Z | Work:Introduction | Free              |

Renaming the columns we can give some more sensible output:

| start_timestamp      | end_timestamp        | activity          | next_activity     |
|----------------------|----------------------|-------------------|-------------------|
| 2018-08-08T17:00:00Z | 2018-08-08T18:00:00Z | Work:Writing      | Work:Introduction |
| 2018-08-08T18:00:00Z | 2018-08-08T19:00:00Z | Work:Introduction | Free              |

This should then be trivial to compute extra values on and plot into some figures:

    require('plyr')
    d$time_spent <- d$end_timestamp - d$start_timestamp
    s <- ddply(d, 'activity', summarise, time=sum(time_spent))
    pie(s$activity, s$time)


Implementation
--------------

Several implementations of this are easily implemented.

This repository provides two example `tt` program to put rows into the data
file.

One of them is tt.sh a bash implementation that is not as good as the other,
tt.py, which is a python implementation providing several options and commands.

Ideally this also should have good zsh/bash completions to avoid data entry
mistakes.

tt.py
-----

tt.py is still quite rough. Several commands are available:

- `do`, `append`, `new`, `a` and `add` all create a new activity
- `tail`, `show`, ``t` and using no command display the last `n` activities.
- `e`, `edit`, and `vi` all open the file in an editor.
- `flush` clears the file's contents
- `backup` copies the file to the backup location.

A couple of other arguments are possible:

- `-v` increased verbosity
- `-u` display timestamp in UTC
- `-r` display timestamps as UNIX timestamps (seconds since 1970)
- `-d` loads an alternative directory
- `-c` loads an alternative configuration (configurations are not implemented yet, this is just a placeholder)
- `-a` archives old entries. This is not implemented yet, as the requirements are not clear yet.

