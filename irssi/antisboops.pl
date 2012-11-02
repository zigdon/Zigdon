# Anti sb oops - Prevent replying to stuff in scrollback
# -- 0.5 (2012-03-07) --by Nemo
# * Add a statusbar item which will indicate when "paged up". 
#   (distinct from the 'more' item which only indicates activity when paged up)
#   Usage: add "pgupind" item to statusbar.
#	(eg: /statusbar prompt add -before input pgupind)
#   Configuration: /set pgupind_str
#   BUGS:
#   * does not understand split windows
#   * indicator appears/dissapears a keypress later than expected
#
# -- 0.4 (2009-08-19)
# * Don't block if the input line starts with /. This also means you can type
#   stuff by entering "/ text" in addition to the double-tap method.
#
# -- 0.3 (2009-08-19)
# * A terminal bell will be sent at you to alert you to your error. Can be
#   turned off with the setting antisboops_beep.
#
# -- 0.2 (2009-08-19)
# * Adds a "double-press" timeout. If you press enter twice within this many
#   miliseconds, the line will get sent anyway. Setting this to 0 should
#   disable this feature. Setting is antisboops_doublepress_time.
#
# -- 0.1 (2009-08-19)
# * Does what it says on the tin.
# * Won't stop you from pasting or causing output in other ways than pressing
#   enter.

$VERSION = "0.5";
%IRSSI = (
    authors     => "Jonas Haggqvist",
    contact     => "rasher@rasher.dk",
    name        => "antisboops",
    description => "Prevent accidental typing while in scrollback",
    license     => "BSD license without advertising clause",
    url         => "http://rasher.dk/pub/irssi",
);

#use strict;
use Irssi::TextUI;
use Time::HiRes qw ( time );


our $ENTER = 10;
our $lastenter = 0;

sub check_enter {
    my ($key) = @_;
    my $atbottom = Irssi::active_win()->view()->{bottom};

    if (!$atbottom) {
	$pgupind_str = Irssi::settings_get_str('pgupind_str');
    } else {
	$pgupind_str="";
    }
    Irssi::statusbar_items_redraw('pgupind');

    my $now = time();
    my $input = Irssi::parse_special('$L');
    if (
        $key eq $ENTER
            and !($input =~ /^\//)
            and !$atbottom
            and $now > $lastenter + (Irssi::settings_get_int('antisboops_doublepress_time') / 1000)
    ) {
        $lastenter = $now;
        Irssi::signal_stop();
        if (Irssi::settings_get_bool('antisboops_beep')) {
            Irssi::command("beep");
        }
    }
}

sub pgupStatusbar() {
	my ($item, $get_size_only) = @_;
	$item->default_handler($get_size_only, $pgupind_str, undef, 1);
}

# pageup indicator in statusbar
Irssi::statusbar_item_register('pgupind', '$0', 'pgupStatusbar');

# Signal hooks
Irssi::signal_add_first('gui key pressed', 'check_enter');

# Settings
Irssi::settings_add_int('misc', 'antisboops_doublepress_time', 200);
Irssi::settings_add_bool('misc', 'antisboops_beep', 1);
Irssi::settings_add_str('misc', 'pgupind_str', '%3%k*');

