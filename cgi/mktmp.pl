#!/usr/bin/perl -wT

use strict;
use CGI;

my $q = new CGI;
print $q->header;

print "<html><body>";
my $dir = "/var/ssl_www/cgi-bin/onetime";
if ($q->param('id') =~ /(\d+)/) {
  my $id = $1;
  if (open(NOTE, "$dir/$1")) {
    print "<pre>";
    print <NOTE>;
    close NOTE;
    unlink "$dir/$1";
    print "</pre><br />";
    print "This note is now deleted from the server, do NOT refresh this page.<br />";
  } else {
    print "This link is no longer valid. ";
    print "You can enter a new one <a href=\"/cgi-bin/mktmp.pl\">here</a>.";
  }
} elsif ($q->param('note') and $q->param('note') =~ /(.*)/s) {
  my $note = $1;
  $note =~ s/&/&amp;/g;
  $note =~ s/</&lt;/g;
  $note =~ s/>/&gt;/g;

  my $id = int(rand(1e8));
  my $count = 100;
  while (open ID, "$dir/$id") {
    $id = int(rand(1e8));
    last unless --$count;
  }

  if ($count == 0) {
    print "Failed to save note, sorry.  Try again later.";
  } else {
    if (open(ID, ">$dir/$id")) {
      print ID $note;
      close ID;

      print "Your note has been saved.  Please send this link to the recipient:<br />";
      print "<code>https://irc.peeron.com/cgi-bin/mktmp.pl?id=$id</code><br />";
      print "This link will work one time only - it will automatically be deleted after it's visited.";
    } else {
      print "Failed to save your note: $!.  Try again later.";
    }
  }
} else {
  print <<HTML;
      <html><head><title>Leave a "secure" note</title></head>
      <body><form>
      Enter text:<br />
      <textarea name="note" cols="60" rows="20"></textarea><br />
      <input type="submit" value="Save note" />
      </form>
HTML
}

print "</body></html>";
