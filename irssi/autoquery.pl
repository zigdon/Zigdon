use strict;
use vars qw($VERSION %IRSSI);

use Irssi;
$VERSION = '0.01';
%IRSSI   = (
    authors     => 'zigdon',
    contact     => 'zigdon@gmail.com',
    name        => 'query autonumber',
    description => 'Allows more control on the number new windows get',
    license     => 'GNU General Public License',
    url         => 'https://github.com/zigdon/Zigdon/blob/master/irssi/autoquery.pl',
);

use Data::Dumper;
$Data::Dumper::indent = 1;

my %map = ();

sub dump {
  my $name = shift;
  return sub {
    print "vvvvvvvvvvvvvvvvvvvvvvv $name vvvvvvvvvvvvvvvvvvvvvvv\n";
    print Dumper \@_;
    print "^^^^^^^^^^^^^^^^^^^^^^^ $name ^^^^^^^^^^^^^^^^^^^^^^^\n";
  }
}

sub wic {
  my ($win, $query) = @_;

  my $name = $query->{name};

  return unless exists $map{$name};

  $win->command("window number $map{$name}");
}

sub load_map {
  my @map = split /[:, ]/, Irssi::settings_get_str("window_auto_number");
  my %newmap;
  my %rmap;

  while (@map) {
    my $k = shift @map;
    my $v = shift @map;

    unless ($k and $v) {
      Irssi::print("*** ERROR: window_auto_number should be of the format 'name:num,name:num'.");
      last;
    }
    if (exists $rmap{$v}) {
      Irssi::print("*** ERROR: window_auto_number assigns both $k and $rmap{$v} to $v.");
    }

    $newmap{$k} = $v;
    $rmap{$v} = $k;
  }

  %map = ( %newmap );
}

Irssi::settings_add_str("lookandfeel", "window_auto_number", "");
&load_map();

#Irssi::signal_add("window created", &dump("w+"));
#Irssi::signal_add("window changed", &dump("wc"));
#Irssi::signal_add("window changed automatic", &dump("wca"));
#Irssi::signal_add("window refnum changed", &dump("wrc"));
# Irssi::signal_add("window item changed", &dump("wic"));
Irssi::signal_add("window item changed", \&wic);
Irssi::signal_add("setup changed", \&load_map);
