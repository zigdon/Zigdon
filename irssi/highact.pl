use Irssi;
use strict;

use vars qw/$VERSION %IRSSI/;

$VERSION = '0.01';
%IRSSI = (
  author => 'zigdon',
  contact => 'zigdon@gmail.com',
  name => 'highact',
  descriptions => 'Define high-activity command that will switch to a window with activity > high_activity_threshold',
);

sub high_act {
  foreach my $win (sort {$a->{refnum} <=> $b->{refnum}} Irssi::windows()) {
    next unless $win->{active};
    next unless $win->{data_level} > 0;
    next unless $win->{refnum} > Irssi::settings_get_int("high_activity_threshold");

    $win->set_active();
    last;
  }
}

Irssi::settings_add_int( 'misc', 'high_activity_threshold', 19 );
Irssi::command_bind( 'high_activity', 'high_act' );
