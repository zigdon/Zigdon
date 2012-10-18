# Hilight people who I've addressed in the last few minutes

use Irssi;
use vars qw($VERSION %IRSSI); 
$VERSION = "0.01";
%IRSSI = (
    authors	=> "zigdon",
    contact	=> "zigdon\@gmail.com", 
    name	=> "conversation",
    description	=> "Hilight nicks who you've responsded to recently",
    license	=> "Creating Commons Attribution-ShareAlike 3.0",
    url		=> "https://github.com/zigdon/Zigdon/blob/master/irssi/conversation.pl",
    changed	=> "2011-02-23 12:50 PST",
);

my %hilights;
my $last_cleanup = time;

sub sig_incoming {
  my ($server, $text, $nick, $who, $channel) = @_;

  if (time - $last_cleanup >
      Irssi::settings_get_int("conversation_timeout")) {
    &cleanup();
  }

  return unless exists $hilights{"$channel/$nick"};

  Irssi::signal_continue($server, $text, "\c_$nick\co", $who, $channel);
}

sub sig_outgoing {
  my ($server, $text, $channel) = @_;

  return unless $text =~ /^(\w+):/;
  $hilights{"$channel/$1"} = time;
}

sub cleanup {
  foreach (keys %hilights) {
    next unless time - $hilights{$_} >
         Irssi::settings_get_int("conversation_timeout");
    delete $hilights{$_};
  }
}

Irssi::settings_add_int("conversation", "conversation_timeout", 300);

Irssi::signal_add('message own_public', 'sig_outgoing');
Irssi::signal_add('message public', 'sig_incoming');
