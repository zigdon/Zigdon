# Anti sb oops - Prevent replying to stuff in scrollback, accidental /cmd

$VERSION = '0.6';
%IRSSI = (
    authors     => 'Jonas Haggqvist, zigdon',
    contact     => 'rasher@rasher.dk, zigdon@foonetic',
    name        => 'antisboops',
    description => 'Prevent accidental commands, typing while in scrollback',
    license     => 'BSD license without advertising clause',
    url         => 'https://github.com/zigdon/Zigdon/blob/master/irssi/antisboops.pl',
);

#use strict;
use Irssi::TextUI;
use Time::HiRes qw ( time );

our $ENTER = 10;
our $lastenter = 0;
our $re = qr//;

sub deny {
    my $now = time();
    return 0 unless $now > $lastenter + (Irssi::settings_get_int('antisboops_doublepress_time') / 1000);

    $lastenter = $now;
    Irssi::signal_stop();
    if (Irssi::settings_get_bool('antisboops_beep')) {
        Irssi::command('beep');
    }

    return 1;
}

sub check_enter {
    my ($key) = @_;

    my $input = Irssi::parse_special('$L');
    return unless $key eq $ENTER;

    if (Irssi::settings_get_bool('antisboops_scrollback')) {
        my $atbottom = Irssi::active_win()->view()->{bottom};

        if (!$atbottom) {
            $pgupind_str = Irssi::settings_get_str('pgupind_str');
        } else {
            $pgupind_str='';
        }
        Irssi::statusbar_items_redraw('pgupind');

        if ($input !~ /^\// and not $atbottom) {
            return if &deny();
        }
    }

    if ($re and Irssi::settings_get_bool('antisboops_commands')) {
        if ($input =~ $re) {
            return if &deny();
        }
    }
}

sub pgupStatusbar() {
	my ($item, $get_size_only) = @_;
	$item->default_handler($get_size_only, $pgupind_str, undef, 1);
}

sub update_cmd_re {
    my @commands = split /\s*,\s*/, Irssi::settings_get_str('antisboops_command_list');
    my $new = join '|', @commands;
    $re = qr#.+/(?:$new)(?:\s*\S+)?$#i;
}

# pageup indicator in statusbar
Irssi::statusbar_item_register('pgupind', '$0', 'pgupStatusbar');

# Signal hooks
Irssi::signal_add_first('gui key pressed', 'check_enter');
Irssi::signal_add('setup changed', \&update_cmd_re);

# Settings
Irssi::settings_add_int('misc', 'antisboops_doublepress_time', 200);
Irssi::settings_add_bool('misc', 'antisboops_scrollback', 1);
Irssi::settings_add_bool('misc', 'antisboops_commands', 1);
Irssi::settings_add_str('misc', 'antisboops_command_list', 'w,win,go,sb');
Irssi::settings_add_bool('misc', 'antisboops_beep', 1);
Irssi::settings_add_str('misc', 'pgupind_str', '%3%k*');

&update_cmd_re()

# vim: set ts=4 sw=4:
