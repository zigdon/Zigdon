#!/usr/bin/perl -w

# Written by Dan Boger <zigdon@gmail.com>

use strict;
use vars qw($VERSION %IRSSI);

$VERSION = "0.1";
%IRSSI = (
    authors     => 'Dan Boger',
    contact     => 'zigdon@gmail.com',
    name        => 'comlink',
    description => 'Mangle < comlink> <user> to < <user>>',
    url         => 'https://github.com/zigdon/Zigdon/blob/master/irssi/comlink.pl',
);

use Irssi;
use Irssi::Irc;

sub cleanup {
  my ($server, $msg, $nick, $address, $target) = @_;


  if ($nick eq 'comlink' and $address =~ /^comlink@/ and $msg =~ s/^(<\w+>)\s+//) {
    $nick = $1;
    Irssi::signal_emit("message public", $server, $msg, $nick, $address, $target);
    Irssi::signal_stop();
    return;
  }
}

Irssi::signal_add('message public', \&cleanup);

