
$VERSION = "0.1";
%IRSSI = (
    authors     => "zigdon",
    contact     => "zigdon\@gmail.com",
    name        => "nsfw",
    description => "force all links sent to (some) channels to be marked SFW/NSFW",
    license     => "GPLv2 or later",
    url         => "https://github.com/zigdon/Zigdon/tree/master/irssi/nsfw.pl",
);

use strict;

my $ENTER = 10;

sub check_enter {
    my ($key) = @_;
    my $text = Irssi::parse_special '$L', undef, 0;
    my $channel = Irssi::parse_special '$C', undef, 0;
    if (
         $key eq $ENTER
            and ( Irssi::settings_get_str('nsfw_channels') eq '*'
                  or Irssi::settings_get_str('nsfw_channels') =~ /\Q$channel/i ) # channel is in the list
            and $text =~ m#https?://#i # input matches http://
            and $text !~ /\bn?sfw\b/i # input doesn't match N?SFW
    ) {
        Irssi::signal_stop();
        if (Irssi::settings_get_bool('nsfw_beep')) {
            Irssi::command("beep");
        }
    }
}

# Signal hooks
Irssi::signal_add_first('gui key pressed', 'check_enter');

# Settings
Irssi::settings_add_str('misc', 'nsfw_channels', "*");
Irssi::settings_add_bool('misc', 'nsfw_beep', 1);
