use strict;
use vars qw($VERSION %IRSSI);

use Irssi;
$VERSION = '0.01';
%IRSSI   = (
    authors     => 'zigdon',
    contact     => 'zigdon@gmail.com',
    name        => 'fix slash command errors',
    description => 'try to remove leading spaces from slash commands',
    license     => 'GNU General Public License',
);

sub strip_spaces {
    my $now = time();
    if ($_[0] =~ s#^ +/(\S)#/$1#) {
      Irssi::signal_emit('send command', @_);
      Irssi::signal_stop();
    }
}

Irssi::signal_add_first('send command', 'strip_spaces');
