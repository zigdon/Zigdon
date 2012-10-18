use strict;
use Irssi;
use Irssi::Irc;
use vars qw($VERSION %IRSSI);

$VERSION = "0.1";
%IRSSI   = (
    authors     => 'Dan Boger',
    contact     => 'zigdon@gmail.com',
    name        => 'shutup',
    description => 'Shut up annoying users.  Usage: /shutup nick; /nonick nick; /shutup <sec> nick',
    license     => 'GNU GPL v2',
    url         => 'https://github.com/zigdon/Zigdon/blob/master/irssi/shutup.pl',
    changed     => 'Thu Jun  5 14:57:04 PDT 2008',
);

sub cmd_shutup {
    my ( $data, $server, $win ) = @_;

    unless ( $server and $server->{connected} ) {
        Irssi::active_win()->print("Not connected to server!");
        return;
    }

    unless ( $win and $win->{type} eq 'CHANNEL' ) {
        Irssi::active_win()->print("Can't ban people out of channel!");
        return;
    }

    my $channel = $server->channel_find( $win->{name} );
    my $timeout = Irssi::settings_get_int("shutup_length") || 60;

    $data =~ s/^\s+//;
    if ($data =~ s/^(\d+)\s+//) {
      $timeout = $1;
    }
    $data =~ s/\s.*//;

    my $nick    = $channel->nick_find($data);

    if ($nick) {
        Irssi::active_win()->print("Shutting up $data for $timeout seconds");
        my $min = int ($timeout/60);
        if ($min <= 1) {
          $min = "a minute";
        } else {
          $min = "$min minutes";
        }

        # $win->command("MSG $win->{name} Shut up, $data.  Come back in $min");
                      
        &tmpban($server, $win->{name}, $nick->{host}, $timeout, 'q', 'n');
    } else {
        Irssi::active_win()->print("Can't find $data in $channel->{name}");
        return;
    }
}

sub cmd_nonick {
    my ( $data, $server, $win ) = @_;

    unless ( $server and $server->{connected} ) {
        Irssi::active_win()->print("Not connected to server!");
        return;
    }

    unless ( $win and $win->{type} eq 'CHANNEL' ) {
        Irssi::active_win()->print("Can't ban people out of channel!");
        return;
    }

    my $channel = $server->channel_find( $win->{name} );
    my $timeout = Irssi::settings_get_int("shutup_length") || 60;

    $data =~ s/^\s+//;
    if ($data =~ s/^(\d+)\s+//) {
      $timeout = $1;
    }
    $data =~ s/\s.*//;

    my $nick    = $channel->nick_find($data);

    if ($nick) {
        &tmpban($server, $win->{name}, $nick->{host}, $timeout, 'n');
        Irssi::active_win()->print("Nickblocking $data for $timeout seconds");
    } else {
        Irssi::active_win()->print("Can't find $data in $channel->{name}");
        return;
    }
}

sub tmpban {
  my ($server, $chan, $nick, $timeout, @bans) = @_;

  my $bans;
  foreach (@bans) {
    $bans = "b$bans ~$_:$nick";
  }

  $server->send_raw("mode $chan +$bans");

  Irssi::timeout_add_once(
      $timeout * 1000,
      sub { $server->send_raw("mode $chan -$bans"); },
      ""
  );
}

Irssi::settings_add_int( "misc", "shutup_length", 60 );
Irssi::command_bind( "shutup", "cmd_shutup" );
Irssi::command_bind( "nonick", "cmd_nonick" );
