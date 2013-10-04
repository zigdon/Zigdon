.mode csv
.header on
.output people-all.csv
select Name, count(Name), sum(Incoming)
from textmessage t 
left join textconversation v on t.textconversationid = v.textconversationid
left join contact c on c.contactid = v.contactid
group by name
order by count(name) desc;

.output people-2009.csv
select Name, count(Name), sum(Incoming)
from textmessage t 
left join textconversation v on t.textconversationid = v.textconversationid
left join contact c on c.contactid = v.contactid
where timerecordedutc > "2009-01-01" and timerecordedutc < "2010-01-01"
group by name
order by count(name) desc;

.output people-2010.csv
select Name, count(Name), sum(Incoming)
from textmessage t 
left join textconversation v on t.textconversationid = v.textconversationid
left join contact c on c.contactid = v.contactid
where timerecordedutc > "2010-01-01" and timerecordedutc < "2011-01-01"
group by name
order by count(name) desc;

.output people-2011.csv
select Name, count(Name), sum(Incoming)
from textmessage t 
left join textconversation v on t.textconversationid = v.textconversationid
left join contact c on c.contactid = v.contactid
where timerecordedutc > "2011-01-01" and timerecordedutc < "2012-01-01"
group by name
order by count(name) desc;

.output people-2012.csv
select Name, count(Name), sum(Incoming)
from textmessage t 
left join textconversation v on t.textconversationid = v.textconversationid
left join contact c on c.contactid = v.contactid
where timerecordedutc > "2012-01-01" and timerecordedutc < "2013-01-01"
group by name
order by count(name) desc;

.output people-2013.csv
select Name, count(Name), sum(Incoming)
from textmessage t 
left join textconversation v on t.textconversationid = v.textconversationid
left join contact c on c.contactid = v.contactid
where timerecordedutc > "2013-01-01" and timerecordedutc < "2014-01-01"
group by name
order by count(name) desc;

.output dates.csv
select date(timerecordedutc) date, count(date(TimeRecordedUTC)) num
from textmessage t 
left join textconversation v 
on t.textconversationid = v.textconversationid 
left join contact c on c.contactid = v.contactid
group by date;
