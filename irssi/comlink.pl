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

my $once = 0;
sub cleanup {
  my ($server, $msg, $nick, $address, $target) = @_;

  unless ($once++) {
    use Data::Dumper;
    print Dumper \@_;
  }

  if ($nick eq 'comlink') {
    $msg =~ s/^<(\w+)>//;
    if ($1) {
      Irssi::print("changed -> $1\n");
      $nick = "<$1>";
      Irssi::signal_emit("message public", $server, $msg, $nick, $address, $target);
      Irssi::signal_stop();
      return;

    }
  }
}
