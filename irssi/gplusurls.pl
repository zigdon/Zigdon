#!/usr/bin/perl -w

# Written by Dan Boger <zigdon@gmail.com>

use strict;
use vars qw($VERSION %IRSSI);

$VERSION = "0.1";
%IRSSI = (
    authors     => 'Dan Boger',
    contact     => 'zigdon@gmail.com',
    name        => 'gplusurls',
    description => 'Fixes g+ URLs before posting to channel',
    license     => 'GNU GPLv2 or later',
    url         => 'https://github.com/zigdon/Zigdon/blob/master/irssi/g+.pl',
);

use Irssi;
use Irssi::Irc;

use Data::Dumper; $Data::Dumper::indent=1;

sub cleanup {
  my ($line, $server, $witem) = @_;

  if ($line =~ s{^https?://plus\.google\.com/u/\d+/}{https://plus.google.com/}ig) {
    Irssi::signal_emit("send text", $line, $server, $witem);
    Irssi::signal_stop();
    return;
  }

}

Irssi::signal_add('send text', \&cleanup);
