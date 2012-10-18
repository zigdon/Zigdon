use strict;
use vars qw($VERSION %IRSSI);

use Irssi;
$VERSION = '1.00';
%IRSSI   = (
    authors     => 'zigdon',
    contact     => 'zigdon@gmail.com',
    name        => 'Bucket teaching script',
    description => 'Send a PM to bucket, and echo it to the current channel, if bucket is not already there',
    license     => 'GNU General Public License',
    url         => 'https://github.com/zigdon/Zigdon/blob/master/irssi/bucket.pl',
);

my %channels = map {$_=>1} qw/#xkcd #hops #bucket/;

sub bucket {
  my ($data, $server, $witem) = @_;

  if ($witem->{type} eq 'CHANNEL') {
    $witem->command("/say bucket: $data");
    unless (exists $channels{$witem->{name}}) {
      $witem->command("/msg bucket $data");
    }
  }
}

Irssi::command_bind('bucket', \&bucket);
