# Display titles of URLs, generate HTML page
#
# based on url_log 0.2 by Thomas Graf <tgraf@europe.com>
#
# infected with the gpl virus
#
# Dan Boger <zigdon@gmail.com>
# version: 1.0

use strict;
use Irssi;
use Irssi::Irc;
use File::Temp qw/tempfile/;
use File::Copy;

use vars qw/$VERSION %IRSSI/;
$VERSION = "1.1";
%IRSSI   = (
    authors => 'Dan Boger, based on code by Thomas Graf',
    contact => 'zigdon@gmail.com',
    name    => 'url_log',
    description => 'Fetches HTML pages titles, generates an HTML index',
    license => 'GNU GPLv2 or later',
    url     => 'https://github.com/zigdon/Zigdon/blob/master/irssi/url_log.pl',
);

use LWP;
use LWP::UserAgent;
use HTML::TreeBuilder;

use POSIX qw(strftime);

use strict;
$SIG{CHLD} = 'IGNORE';

my %seen;
my @url_data;
my %channels;
my $user_agent = new LWP::UserAgent( max_size => 8196 );
my $last_save_time = 0;
my $pid;

$user_agent->agent("IrssiUrlLog/$VERSION");

sub expand {
    my ( $string, %format ) = @_;
    my ( $exp, $repl );
    $string =~ s/%$exp/$repl/g while ( ( $exp, $repl ) = each(%format) );
    return $string;
}

sub print_msg {
    Irssi::active_win()->print("@_");
}

sub title {
    my ($url) = @_;

    # get the content-type first, so we only check titles for html
    my $req = new HTTP::Request HEAD => $url;
    my $res = $user_agent->request($req);
    return "<no result for head>" unless $res;
    return "Content type:"
      . $res->header("Content_type") . " ("
      . $res->header("Content_length")
      . " bytes)"
      unless $res->header("Content_type") =~ m#text/|application/x-httpd-php#;

    $req = new HTTP::Request GET => $url;
    $res = $user_agent->request($req);
    return "<no result>" unless $res;

    my $tree = HTML::TreeBuilder->new_from_content( $res->content );
    return "<no html>" unless $tree;

    my $title = $tree->look_down( _tag => "title" );
    $title = $title->as_text if $title;
    $tree->delete;

    return $title || "<no title>";
}

#
# called if url is detected, should get the title
#
sub do_auto_title {
    my ( $url, $window ) = @_;

    return if ( $url !~ /^https?:\/\// );

    return if $seen{$url} and time - $seen{$url} < 600;
    $seen{$url} = time;

    my ( $fh, $filename ) = tempfile();
    $pid = fork();
    Irssi::pidwait_add($pid);

    if ($pid) { # parent
        Irssi::timeout_add_once( 1000, 'monitor_log', [ $filename, $window ] );
    }
    elsif ( defined $pid ) { # child
        close STDIN;
        close STDOUT;
        close STDERR;
        my $format = Irssi::settings_get_str("url_title_format");
        my $title  = title($url);
        $format =~ s/\%u/$url/g;
        $format =~ s/\%t/$title/eg;
        print $fh "$url = $title \t$format";
        close $fh;
        exit;
    }
}

sub monitor_log {
    my ($data) = @_;
    my ( $filename, $window ) = @$data;

    if ( open( FH, $filename ) ) {
        my $line = <FH>;
        chomp $line;
        close FH;

        if ($line) {
            $line =~ s/^(\S+) = ([^\t]+)\t//;
            my ( $url, $title ) = ( $1, $2 );
            $line =~ s/%/%%/g;
            $window->print("$line");
            unlink $filename;

            if ( Irssi::settings_get_str('url_log_html') ) {
                my $i = $#url_data + 1;
                foreach ( reverse @url_data ) {
                    $i--;
                    next unless $_->[3] eq $url;
                    last if $_->[5];
                    $_->[5] = $title;
                    $url_data[$i] = $_;
                    &generate_html;
                    last;
                }
            }

          Irssi::pidwait_remove($pid);
        }
        else {
            Irssi::timeout_add_once( 1000, 'monitor_log',
                [ $filename, $window ] );
        }
    }
}

#
# log url to file
#
sub log_to_file {
    my ( $nick, $target, $text ) = @_;
    my ($lfile) = glob Irssi::settings_get_str("url_log_file");

    if ( open( LFD, ">> $lfile" ) ) {

        my %h = {
            time   => time,
            nick   => $nick,
            target => $target,
            url    => $text
        };

        print LFD expand(
            Irssi::settings_get_str("url_log_format"),
            "s",
            strftime(
                Irssi::settings_get_str("url_log_timestamp_format"), localtime
            ),
            "n", $nick, "t", $target, "u", $text
          ),
          "\n";

        close LFD;
    }
    else {
        print_msg "Warning: Unable to open file $lfile $!";
    }
}

#
# msg handler
#
sub sig_msg {
    my ( $server, $data, $nick, $address ) = @_;
    my ( $target, $text ) = split( / :/, $data, 2 );

    while (
        $text =~ s{
              (^|.*?\s) # $1 - leading comments
              (         # $2 - URL
                 (?:    #    - domain
                    (?:https?://[\w\.-]+   | # stuff starting with http
                    (?:[\w-]+\.){2,}[a-z]+)  # something.like.this
                 )
                 (?:    #    - path (optional)
                    / \S*
                 )?
              )
              ($|\s.*)  # $3 - trailing comments
            }{$1 <URL> $3}xi
      )

    {

        my ( $leading, $url, $trailing ) = ( $1, $2, $3 );
        my $text = $leading || $trailing;
        $text =~ s/.* <URL> //;
        $text =~ s/^\s+|\s+$//g;

        foreach ( keys %seen ) {
            next if time - $seen{$_} < 600;
            delete $seen{$_};
        }

        my $ischannel = $server->ischannel($target);
        my $channel   = $target;
        my $level     = $ischannel ? MSGLEVEL_PUBLIC: MSGLEVEL_MSGS;
        $target = $nick unless $ischannel;
        my $window = $server->window_find_closest( $target, $level );

        if ( Irssi::settings_get_bool("url_log_auto_head") ) {
            do_auto_title( $url, $window );
        }

        if ( Irssi::settings_get_bool("url_log") ) {
            log_to_file( $nick, $target, $url );
        }

        if ( Irssi::settings_get_str('url_log_html') ) {

            # time, chan, who, url, text
            push @url_data,
              [
                time, ( $ischannel ? $channel : "N/A" ),
                $nick, $url, $text, undef
              ];
            $channels{$ischannel ? $channel : "N/A"} ++;
            &generate_html;
            if (
                time - $last_save_time >
                Irssi::settings_get_int('url_log_save_interval') )
            {
                &save_url_data;
            }
        }
    }
}

#
# url command handler
#
sub sig_url {
    my ( $cmd_line, $server, $win_item ) = @_;
    my @args = split( ' ', $cmd_line );

    if ( @args <= 0 ) {
      &help;
        return;
    }

    my $action = lc( shift(@args) );

    if ( $action eq 'save' ) {
        &save_url_data;
        print_msg "URL data saved";
    }
    elsif ( $action eq 'load' ) {
        &load_url_data;
        &generate_html;
        print_msg "URL data loaded";
    }
    elsif ( $action eq 'regenerate' ) {
        &generate_html;
        print_msg "HTML page regenerated";
    }
    elsif ( $action eq 'debug' ) {
        print_msg "URL cache (\%seen): ". scalar keys(%seen) . " urls.";
        print_msg "URL list (\@url_data): ". scalar @url_data . " urls.";
    }
    else {
        print_msg "Unknown action";
    }
}

sub save_url_data {
    my $filename = Irssi::settings_get_str('url_log_data_file');
    unless ( open( SAVE, ">$filename.new" ) ) {
        print_msg "Failed to write $filename.new: $!";
        return;
    }

    foreach (@url_data) {
        next
          if time - $_->[0] >
          Irssi::settings_get_int('url_log_html_days') * 24 * 60 * 60;

        print SAVE join "\t", @$_;
        print SAVE "\n";
    }
    close SAVE;
    move "$filename.new", $filename;
}

sub load_url_data {
    my $filename = Irssi::settings_get_str('url_log_data_file');
    unless ( open( SAVE, $filename ) ) {
        print_msg "Failed to read $filename: $!";
        return;
    }

    @url_data = ();
    while (<SAVE>) {
        chomp;
        my @line = split /\t/, $_, 6;
        next
          if time - $line[0] >
          Irssi::settings_get_int('url_log_html_days') * 24 * 60 * 60;
        push @url_data, [@line];    # time, chan, who, url, text, title
        $channels{$line[1]}++;
    }
    close SAVE;
}

sub generate_html {
    my ( $cmd_line, $server, $win_item ) = @_;
    my @args = split( ' ', $cmd_line );

    my $filename = Irssi::settings_get_str('url_log_html');
    unless ( open( HTML, ">$filename.new" ) ) {
        print_msg "Failed to write $filename.new: $!";
        return;
    }

    binmode HTML, ':utf8';

    print HTML <<EOT;

<html><head><title>URL log for $ENV{USER}</title>
  <style type='text/css'>
    .meta { font-size: small; }
    .who { font-style: italic; }
    .title { font-weight: bold; }
    .text { color: gray; }
    .note { color: gray; font-size: x-small }
    #navbar { background-color: gray; font-size: large; 
              width: 100%; padding: 2px; text-align: center;}
    h2 { border-bottom: thin gray solid; }
  </style>
  <script language='javascript' defer>
  function SelectChannel(chan) {
    links = document.getElementsByTagName("li");
    for (i=0; i<links.length; i++) {
      if (chan == "ALL" || links[i].getElementsByTagName("span")[2].innerHTML == chan) {
        links[i].style.display = "";
      } else {
        links[i].style.display = "none";
      }
    }
  }
  function Toggle(e) {
    u = e.nextSibling;
    if (u.style.display == "none") {
      u.style.display = "block";
    } else {
      u.style.display = "none";
    }
  }
  </script>
</head><body>
EOT
    print HTML "<div id=\"navbar\">| ";
    foreach ("ALL", sort keys %channels) {
       print HTML qq{<a href="#" onClick='SelectChannel("$_")'>$_</a> | };
    }
    print HTML "</div>";
    print HTML qq{<span class="note">Click on the date to fold/unfold</span>};

    my $lastday = undef;

    foreach my $entry ( reverse @url_data ) {
        my ( $time, $chan, $who, $url, $text, $title ) = @$entry;
        $title ||= $url;

        last
          if time - $time >
          Irssi::settings_get_int('url_log_html_days') * 24 * 60 * 60;

        my @time = localtime($time);
        if ( $lastday and $time[3] ne $lastday ) {
            print HTML "</ul>\n";
        }

        if ( not $lastday or $time[3] != $lastday ) {
            my @wday =
              qw/Sunday Monday Tuesday Wednesday Thursday Friday Saturday/;
            printf HTML '<h2 class="date" onclick="Toggle(this)">%02d/%02d/%02d - %s</h2>',
              $time[4] + 1, $time[3], $time[5] % 100, $wday[ $time[6] ],
              join "", $time[5]+1900, $time[4]+1, $time[3];
            if ($lastday) {
              print HTML qq{<ul style="display: none">};
            } else {
              print HTML "<ul>";
            }
            $lastday = $time[3];
        }

        $title =~ s/&/&amp;/g;
        $title =~ s/</&lt;/g;
        $title =~ s/>/&gt;/g;
        $url = "http://$url" unless $url =~ m/^http/;

        print HTML '<li> <span class="meta">[ ';
        printf HTML '<span class="time">%02d:%02d</span> |', @time[ 2, 1 ];
        print HTML qq{ <span class="channel">$chan</span> |};
        print HTML qq{ <span class="who">$who</span> ]</span> };
        print HTML qq{<a href="$url" class="url">$title</a>} if $title;
        print HTML qq{ - <span class="text">$text</span> }   if $text;
        print HTML "</li>\n";
    }
    print HTML "</ul></body></html>\n";
    close HTML;

    move( "$filename.new", $filename );
    #Irssi::print("$filename updated");
}

sub help {
  Irssi::print($_) foreach (
    "url_log will keep track of any URLs posted, looking up the title of each.",
    "For basic usage, no settings are required.  However, some advanced features",
    "are only available once configured:",
    "",
    "log to file:",
    "  url_log (on/off)                  - log urls to a file",
    "  url_log_file (path)               - location of the url log file",
    "  url_log_timestamp_format (format) - how the timestamp should be recorded",
    "display title:",
    "  url_log_auto_head (on/off) - automatically fetch and display the title",
    "                               of URLs",
    "  url_title_format (format)  - how automatically fetched titles should",
    "                               be displayed",
    "HTML page generator:",
    "  url_log_html (path)             - where should the html page be saved",
    "  url_log_save_interval (seconds) - how often should the data be saved",
    "  url_log_html_days (days)        - how many days back should the page display",
#   "  url_log_html_images (on/off)    - should images be displayed inline",
    "",
    "Commands:",
    "  load        - load url datafile",
    "  save        - save url datafile",
    "  regenerate  - regenerate html page",
  );
}

Irssi::command_bind( 'url',  'sig_url' );
Irssi::command_bind( 'quit', 'save_url_data' );
Irssi::signal_add_first( 'event privmsg', 'sig_msg' );

# log to file
Irssi::settings_add_bool( "url_log", "url_log",           1 );
Irssi::settings_add_str( "url_log", "url_log_file", "$ENV{HOME}/.irssi/url.log" );
Irssi::settings_add_str( "url_log", "url_log_timestamp_format", '%c' );
Irssi::settings_add_str( "url_log", "url_log_format",           '%s %n %t %u' );

# display title
Irssi::settings_add_bool( "url_log", "url_log_auto_head", 1 );
Irssi::settings_add_str( "url_log", "url_title_format",     '%u = %t' );

# generate html page
Irssi::settings_add_str( "url_log", "url_log_data_file",
    "$ENV{HOME}/.irssi/url_log.data" );
Irssi::settings_add_str( "url_log", "url_log_html", "$ENV{HOME}/public_html/url_log/index.html" );
Irssi::settings_add_int( "url_log", "url_log_save_interval", 300 );
Irssi::settings_add_int( "url_log", "url_log_html_days",     7 );
Irssi::settings_add_int( "url_log", "url_log_html_images",   0 );

if ( Irssi::settings_get_str('url_log_data_file') ) {
    &load_url_data;
    $last_save_time = time;
    &generate_html;
}
