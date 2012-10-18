# based on http://the-timing.nl/Projects/Irssi-BitlBee/bitlbee_join_notice.pl,
# adjusted to general PMs
#

use strict;

use vars qw($VERSION %IRSSI);

$VERSION = '1.0';
%IRSSI = (
    authors     => 'Dan Boger (aka zigdon)',
    contact     => 'zigdon@gmail.com',
    name        => 'join_notice',
    description => 'Print a message in PM windows when the person reconnects to
                    the network',
    license => 'GPLv2',
    url     => 'https://github.com/zigdon/Zigdon/blob/master/irssi/join_notice.pl',
    changed => '2008-11-20',
);

my $last;

sub event_join {
  my ($server, $channel, $nick, $address) = @_;
  my $window = Irssi::window_find_item($nick);
  if($window and $nick ne $last){
    $window->printformat(MSGLEVEL_JOINS, 'join', $nick, $address); 
    $last = $nick;
  }
}

Irssi::signal_add("event join", "event_join");
Irssi::theme_register([
  'join', '{channick_hilight $0} {chanhost $1} has reconnected',
]);


