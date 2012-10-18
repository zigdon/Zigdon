# Print hilighted messages & private messages to window named "hilight"
# for irssi 0.7.99 by Timo Sirainen
# Updated to avoid hilights form bitlbee -- zigdon
use Irssi;
use vars qw($VERSION %IRSSI); 
$VERSION = "0.01";
%IRSSI = (
    authors	=> "Timo \'cras\' Sirainen",
    contact	=> "tss\@iki.fi", 
    name	=> "hilightwin",
    description	=> "Print hilighted messages & private messages to window named \"hilight\"",
    license	=> "Public Domain",
    url		=> "https://github.com/zigdon/Zigdon/blob/master/irssi/hilightwin.pl",
    changed	=> "2002-03-04T22:47+0100",
);

my $mc_nick = "zigdon";

sub sig_printtext {
  my ($dest, $text, $stripped) = @_;

  if (($dest->{level} & (MSGLEVEL_HILIGHT|MSGLEVEL_MSGS)) and
      (($dest->{level} & MSGLEVEL_NOHILIGHT) == 0) and
      ($dest->{level} & MSGLEVEL_PUBLIC) and
      ($dest->{target} ne "#services") and
      ($dest->{target} ne "&bitlbee")) {
    $window = Irssi::window_find_name('hilight');

    if ($dest->{level} & MSGLEVEL_PUBLIC) {
      $text = $dest->{target}.": ".$text;
    }
    if ($window) {
      $window->print(sprintf('%02d:%02d %s', (localtime)[2,1], $text), MSGLEVEL_NEVER);
    }
  }
}

$window = Irssi::window_find_name('hilight');
Irssi::print("Create a window named 'hilight'") if (!$window);

Irssi::signal_add('print text', 'sig_printtext');
