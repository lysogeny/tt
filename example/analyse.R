#!/usr/bin/env Rscript
# Example analysis for the tt file

library('plyr')
library('ggplot2')

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

theme_set(theme_minimal())

d <- read.table('~/Cloud/tt/time.txt')
names(d) <- c('timestamp', 'activity')
d$timestamp <- as.POSIXct(d$timestamp, origin='1970-01-01')
d$level <- sapply(as.character(d$activity), function(x) length(strsplit(x, ':')[[1]]))

# This plot is silghtly weird. Something is wrong here
ggplot(d) + geom_line(aes(timestamp, level, colour=activity), size=10)

seg <- segmentify(d)
seg <- seg[1:5]
names(seg) <- c('start', 'activity', 'level', 'end', 'next_activity')
seg$length <- seg$end-seg$start

tab <- ddply(seg, 'activity', summarise,
             total_time=sum(length),
             mean_time=mean(length))
tab$perc_time <- as.numeric(tab$total_time) / as.numeric(sum(tab$total_time))
tab

# Some example plots
ggplot(tab) + geom_bar(aes(activity, total_time), stat='identity')
ggplot(tab) + geom_bar(aes('', total_time, fill=activity), stat='identity')

pie(tab$perc_time, labels=paste(round(tab$perc*100,1), tab$activity), main='Time proportions spent')

