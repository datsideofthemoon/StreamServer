window.StreamClient = {};
////////////////////////
//Class Playlist////////
////////////////////////
StreamClient.Navigation = function (StartFrom)
{
    //view.page could be: index,library,folders,search,settings,statistics,about
    //{page:'library',data:{subpage:'random',id:0}} - random page
    //{page:'library',data:{subpage:'artist',id:0}} - all artists
    //{page:'library',data:{subpage:'artist',id:75}} - 75 artist's albums
    //{page:'library',data:{subpage:'album',id:0}} - all albums
    //{page:'library',data:{subpage:'album',id:85}} - 85 album's songs
    //{page:'library',data:{subpage:'year',id:2005}} - songs for 2005 y
    //{page:'library',data:{subpage:'genre',id:0}} - all genres
    //{page:'library',data:{subpage:'genre',id:85}} - 85 genre's songs
    //{page:'library',data:{subpage:'song',id:85}} - 85 song's info
    //{page:'folders',data:{id:907}} - 907 folder content
    //{page:'search',data:{keyword:'abcde'}} - search result
    //{page:'settings',null} - settings page
    //{page:'about',null} - about page
    //{page:'statistics',null} - stat page

    that = this;
    this.HistoryStack = [];

    this.NavigationOnClick = function (event)
    {
        event.preventDefault();
        var link = this.getAttribute('link');
        var link_arr = link.split('/');

        var sub_page = link_arr[0];
        var idx = link_arr[1];
        var NAV = {};
        switch (sub_page)
        {
            case 'artist':
            case 'album':
            case 'genre':
            case 'song':
            case 'year':
                dat = {subpage: sub_page, id: idx};
                NAV = {page: 'library', data: dat};
                break;
            case 'random':

                break;
            case 'folder':
                dat = {subpage: sub_page, id: idx};
                NAV = {page: 'folders', data: dat};
                break;
            case 'play':

                Playlist.tracks = [];
                Playlist.tracks.push($(this).data('track'));
                Playlist.PlayPlaylist();
                break;
        }

        //console.log('page: '+NAV.page + 'subpage: '+NAV.data.subpage+' id: '+NAV.data.id);
        if (sub_page != 'play')
        {
            Navigation.GoTo(NAV, false);
        }
    }
    this.ShowTracks = function (data)
    {
        var table = $("<table>").attr("class", "table table-striped");
        Playlist.Tracks = data;
        for (var r = 0; r < data.length; r++)
        {
            //var a = $("<a>").attr("link", 'play/' + jsondata[r].id).text(jsondata[r].title);
            var td_title = $('<td>').attr("link", 'play/' + data[r].id).text(data[r].title);
            td_title.data('track', data[r]);
            var td_time = $("<td>").text(data[r].length);
            var td_size = $("<td>").text(data[r].size);
            var row = $("<tr>");
            td_title.appendTo(row);
            td_time.appendTo(row);
            td_size.appendTo(row);
            row.appendTo(table);
        }
        Playlist.Tag.fadeOut('fast', function ()
        {
            Playlist.Tag.html(table).fadeIn('fast');
            $('div#playlist td').on('click', that.NavigationOnClick);
        });
    }
    this.ShowNavigation = function (data, subpage)
    {
        // Playlist['artist+'s'] or Playlist['album'+'s']
        Playlist[subpage + 's'] = data;
        //var table = $("<table>").attr("class", "table table-striped");
        for (var r = 0; r < data.length; r++)
        {
            //var a = $("<a>")
            var row = $("<tr>").html($("<td>").attr("link", subpage + '/' + data[r].id).text(data[r].name));
            row.appendTo(table);
        }
        Playlist.Tag.fadeOut('fast', function ()
        {
            Playlist.Tag.html(table).fadeIn('fast');
            $('div#playlist td').on('click', that.NavigationOnClick);
        });
    }
    this.ShowIndex = function ()
    {
        div = $("<div>").attr("class", "row");//.text('This is index yo.');
        for (i = 0; i < 3; i++)
        {
            $("<div>").attr("class", "col-lg-4").text('some').appendTo(div);

        }

        return div;
    }
    this.GoTo = function (nav, backward)
    {
        // toview={
        //      page,
        //      data  = {
        //              subpage,
        //              id
        //              }
        //        }
        switch (nav.page)
        {
            case 'index':
                var htmlpage = that.ShowIndex();//'This is index page. Here you can see different album art, random songs and other stuff.';
                Playlist.Tag.attr('class', '').html(htmlpage);
                break;
            case 'library':
                var table = $("<table>").attr("class", "table table-striped");
                if (nav.data == null) //page:library data:null
                {
                    table.append($("<tr>").html($("<td>").attr('link', 'genre/0').text('Genres')));
                    table.append($("<tr>").html($("<td>").attr('link', 'artist/0').text('Artists')));
                    table.append($("<tr>").html($("<td>").attr('link', 'album/0').text('Albums')));
                    table.append($("<tr>").html($("<td>").attr('link', 'song/0').text('Songs')));
                    table.append($("<tr>").html($("<td>").attr('link', 'year/0').text('Years')));
                    table.append($("<tr>").html($("<td>").attr('link', 'random').text('Random')));
                    Playlist.Tag.fadeOut('fast', function ()
                    {
                        Playlist.Tag.html(table).fadeIn('fast');
                        $('div#playlist td').on('click', that.NavigationOnClick);
                    });
                }
                else
                {
                    if (nav.data.subpage == 'artist' || nav.data.subpage == 'album' || nav.data.subpage == 'genre' || nav.data.subpage == 'year')
                    {
                        if (nav.data.id == 0)
                        {
                            var url = $SCRIPT_ROOT + '/_' + nav.data.subpage + '/0';
                            $.getJSON(url, {}, function (data) {Navigation.ShowNavigation(data.data);});
                        }
                        else if (nav.data.id > 0)
                        {
                            switch (nav.data.subpage)
                            {
                                case 'artist': //list of albums with artistid=x
                                    $.getJSON($SCRIPT_ROOT + '/_artist/' + nav.data.id, {},
                                        function (data)
                                        {
                                            var jsondata = data.data;
                                            Playlist.albums = jsondata;
                                            for (var r = 0; r < jsondata.length; r++)
                                            {
                                                //var a = $("<a>").attr("link", 'album/' + jsondata[r].id).text(jsondata[r].name);
                                                var row = $("<tr>").html($("<td>").attr("link", 'album/' + jsondata[r].id).text(jsondata[r].name));
                                                row.appendTo(table);
                                            }
                                            Playlist.Tag.fadeOut('fast', function ()
                                            {
                                                Playlist.Tag.html(table).fadeIn('fast');
                                                $('div#playlist td').on('click', that.NavigationOnClick);
                                            });
                                        });
                                    break;
                                case 'album' : //list of tracks
                                case 'year' :
                                case 'genre' :
                                    $.getJSON($SCRIPT_ROOT + '/_' + nav.data.subpage + '/' + nav.data.id, {}, function (data) {Navigation.ShowTracks(data.data);});
                                    break;
                                default:
                                    alert('wrong subpage:' + nav.data.subpage);
                            }
                        }
                    }
                    else if (nav.data.subpage == 'song' && nav.data.id == 0)
                    {
                        $.getJSON($SCRIPT_ROOT + '/_' + nav.data.subpage + '/0', {}, function (data) {Navigation.ShowTracks(data.data);});
                    }
                }
                break;
            case 'folders':
                if (nav.data)
                {
                    var url = $SCRIPT_ROOT + '/_folder/' + nav.data.id;
                }
                else
                {
                    var url = $SCRIPT_ROOT + '/_folder/0'
                }
                $.getJSON(url, {},
                    function (data)
                    {
                        var jsondata = data.data;
                        Playlist.folders = jsondata;

                        var foldersArr = jsondata.folders;
                        var filesArr = jsondata.files;
                        if (foldersArr.length > 0)
                        {
                            var table_folders = $("<table>").attr("class", "table table-striped");
                            for (var r = 0; r < foldersArr.length; r++)
                            {
                                //var a = $("<a>").attr("link", 'folder/' + foldersArr[r].id).text(foldersArr[r].directory);
                                var td = $("<td>").attr("link", 'folder/' + foldersArr[r].id).text(foldersArr[r].directory);
                                var row = $("<tr>").html(td);
                                row.appendTo(table_folders);
                            }
                        }
                        if (filesArr.length > 0)
                        {
                            var table_files = $("<table>").attr("class", "table table-striped");
                            Playlist.Tracks = filesArr;
                            for (var r = 0; r < filesArr.length; r++)
                            {
                                //var a = $("<a>").attr("link", 'play/' + filesArr[r].id).text(filesArr[r].filename);
                                var td_title = $("<td>").attr("link", 'play/' + filesArr[r].id).text(filesArr[r].filename);
                                td_title.data('track', filesArr[r]);
                                var td_time = $("<td>").text(filesArr[r].length);
                                var td_size = $("<td>").text(filesArr[r].size);
                                var row = $("<tr>");
                                td_title.appendTo(row);
                                td_time.appendTo(row);
                                td_size.appendTo(row);
                                row.appendTo(table_files);
                            }
                        }
                        Playlist.Tag.fadeOut('fast', function ()
                        {
                            Playlist.Tag.html('');
                            if (table_folders)
                            {
                                table_folders.appendTo(Playlist.Tag);
                            }
                            if (table_files)
                            {
                                table_files.appendTo(Playlist.Tag);
                            }
                            Playlist.Tag.fadeIn('fast');
                            $('div#playlist td').on('click', that.NavigationOnClick);
                        });
                    });
                break;
            default:
                alert('Cant go to: ' + nav.page);
        }
        if (!backward)
        {
            if (that.CurrentView)
            {
                that.HistoryStack.push(that.CurrentView);
                if (that.CurrentView.data)
                {
                    History.pushState({_index: History.getCurrentIndex(), data: that.CurrentView}, "StreamPlayer - " + that.CurrentView.page + '/' + that.CurrentView.data.subpage, '');
                }
                else
                {
                    History.pushState({_index: History.getCurrentIndex(), data: that.CurrentView}, "StreamPlayer - " + that.CurrentView.page, '');
                }
            }
            else
            {
                History.replaceState({_index: History.getCurrentIndex(), data: nav}, "StreamPlayer - " + nav.page, '');
            }
        }
        that.CurrentView = nav;
    }

    this.GoBack = function ()
    {
        if (that.HistoryStack.length > 0)
        {
            var where = that.HistoryStack.pop();
            that.GoTo(where, true); //go backward
            //History.back()
        }
    }

    //main menu
    $('.nav a').on('click', function (e)
    {
        var link = this.getAttribute('link');
        Navigation.GoTo({page: link, data: null}, false); //go to link
    });

    //back button
    $('#goback').on('click', function (e)
    {
        e.preventDefault();
        Navigation.GoBack();
    });


    // Bind to State Change
    History.Adapter.bind(window, 'statechange', function ()
    {
        var state = History.getState(); // Note: We are using History.getState() instead of event.state

        var currentIndex = History.getCurrentIndex();
        var pushstate = (state.data._index == (currentIndex - 1));
        var backward = (state.data._index < (currentIndex));
        if (!pushstate && !backward)
        {
            that.GoTo(state.data.data, false); //go forward, i think
            //console.log('Forward:', state.data, state.title, state.url);
        }
        if (!pushstate && backward)
        {
            that.GoTo(state.data.data, true);  //go backward
            //console.log('Backward: ', state.data, state.title, state.url);
        }
        else
        {
            //console.log('Just Navigation:', state.data, state.title, state.url);
        }
    });

    this.GoTo(StartFrom, false);
    console.log('*Navigation initialized.');
}

StreamClient.Playlist = function ()
{
    this.Tag = $("#playlist");
    this.albums = [];
    this.artists = [];
    this.tracks = [];
    this.genres = [];
    this.years = [];
    this.NowPlaying = -1;

    this.PlayPlaylist = function ()
    {
        if (Playlist.tracks.length > 0)
        {
            AudioPlayer.Pause();
            AudioPlayer.LoadMedia($SCRIPT_ROOT + '/getmedia/' + Playlist.tracks[0].id + Playlist.tracks[0].format);
            if (AudioPlayer.MediaState == 'loaded')
            {
                AudioPlayer.Play();
            }
            this.NowPlaying = 0;
        }
    }
    this.Shuffle = function ()
    {
        var currentIndex = Playlist.Tracks.length, temporaryValue, randomIndex;
        // While there remain elements to shuffle...
        while (0 !== currentIndex)
        {
            // Pick a remaining element...
            randomIndex = Math.floor(Math.random() * currentIndex);
            currentIndex -= 1;
            // And swap it with the current element.
            temporaryValue = Playlist.Tracks[currentIndex];
            Playlist.Tracks[currentIndex] = Playlist.Tracks[randomIndex];
            Playlist.Tracks[randomIndex] = temporaryValue;
        }
    }

    this.SetSize = function ()
    {
        playerHeight = $('footer').height();
        Playlist.Tag.height(window.innerHeight - playerHeight - 80);
        Playlist.Tag.css("overflow", "auto");
        Playlist.Tag.children('table').width = window.innerWidth - 15;
    };

    this.PlaylistScroll = function ()
    {
        var scrollAmount = Playlist.Tag.scrollTop();
        var documentHeight = Playlist.Tag.children().height();
        var scrollPercent = (scrollAmount / documentHeight) * 100;
        if (scrollPercent > 50)
        {
            preloadAnotherData();
        }
    }
    var preloadAnotherData = function ()
    {
        //TODO: write me
    };

    this.Tag.scroll(this.PlaylistScroll);
    console.log('*Playlist initialized.');
};


///////////////////////////
//Class Slider/////////////
///////////////////////////
StreamClient.Slider = function ()
{
    $('#slider').slider();
    $('#slider').width(window.innerWidth - 150);
    $('#slider').height(11);
    console.log('*Slider initialized.');
    this.Update = function (position, duration)
    {
        //slider update
        $('#slider').slider({
            orientation: "horizontal",
            range: "min",
            max: duration,
            value: position/*,
             slide: refreshSwatch,
             change: refreshSwatch*/
        });
        //time update
        var timeLeft = duration - position;
        var s = timeLeft % 60;
        var m = Math.floor(timeLeft / 60) % 60;
        s = s < 10 ? "0" + s : s;
        m = m < 10 ? "0" + m : m;
        $("div#timeleft").html(m + ":" + s);

        s = parseInt(position % 60);
        m = parseInt((position / 60) % 60);
        s = s < 10 ? "0" + s : s;
        m = m < 10 ? "0" + m : m;
        $("div#timeup").html(m + ':' + s);
    }
};


///////////////////////////
//Class AudioPlayer////////
///////////////////////////
StreamClient.AudioPlayer = function ()
{
    this.AudioElementState = 'notcreated';
    this.IsPlaying = false;

    this.SetState = function (state)
    {
        console.log('AudioElement state: ' + state);
        AudioPlayer.AudioElementState = state;
        AudioPlayer.CanPlay = true;
    }
    this.LoadMedia = function (url)
    {
        if (!!document.createElement('audio').canPlayType)
        {
            AudioPlayer.AudioElement = new Audio();
            AudioPlayer.SetState('created');
            AudioPlayer.MediaState = 'notloaded';
            AudioPlayer.AudioElement.setAttribute('src', url);
            AudioPlayer.format = "audio/mpeg"; //todo: set format of track loaded
            AudioPlayer.AudioElement.setAttribute('type', AudioPlayer.format);
            AudioPlayer.AudioElement.load();

            AudioPlayer.AudioElement.addEventListener("loadstart", function ()
            {
                AudioPlayer.SetState('loadstart');
            }, false);
            AudioPlayer.AudioElement.addEventListener("loadedmetadata", function ()
            {
                AudioPlayer.SetState('loadedmetadata');
            }, false);
            AudioPlayer.AudioElement.addEventListener("loadeddata", function ()
            {
                AudioPlayer.SetState('loadeddata');
            }, false);
            //on finish Load
            AudioPlayer.AudioElement.addEventListener("canplay", function ()
            {
                AudioPlayer.SetState('canplay');
            }, false);
            AudioPlayer.AudioElement.addEventListener("canplaythrough", function ()
            {
                AudioPlayer.SetState('canplaythrough');
            }, false);

            //On timeupdate set time left & up
            AudioPlayer.AudioElement.addEventListener("timeupdate", function ()
            {
                //that.timeleft = document.getElementById('timeleft'),
                AudioPlayer.duration = parseInt(AudioPlayer.AudioElement.duration);
                AudioPlayer.currentTime = parseInt(AudioPlayer.AudioElement.currentTime);
                Slider.Update(AudioPlayer.currentTime, AudioPlayer.duration);
                AudioPlayer.timeLeft = AudioPlayer.duration - AudioPlayer.currentTime;
            }, false);
        }
    }
    this.Play = function ()
    {
        if (AudioPlayer.CanPlay && !AudioPlayer.IsPlaying)
        {
            AudioPlayer.AudioElement.play();
            AudioPlayer.AudioElementState = 'playing';
            AudioPlayer.IsPlaying = true;
        }
    }
    this.Pause = function ()
    {
        if (AudioPlayer.AudioElement)
        {
            AudioPlayer.AudioElement.pause();
        }
        AudioPlayer.AudioElementState = 'paused';
        console.log('AudioPlayer.AudioElementState is: ' + AudioPlayer.AudioElementState);
    }
    console.log('*new AudioPlayer()');
}


////////////////////////////////
//User Interface Events/////////
////////////////////////////////
$("#playbtn").click(function ()
{
    icon = $("#playbtn").children('span');

    //from play to pause
    if (AudioPlayer.CanPlay)
    {
        if (AudioPlayer.IsPlaying)
        {
            icon.attr('class', 'glyphicon glyphicon-play');
            AudioPlayer.Pause();
        }
        else
        {
            icon.attr('class', 'glyphicon glyphicon-pause');
            AudioPlayer.Play();
        }
    }
    icon.html(AudioPlayer.AudioElementState + ' ' + AudioPlayer.MediaState);
});

Slider = new StreamClient.Slider();

Playlist = new StreamClient.Playlist();
Playlist.SetSize();

AudioPlayer = new StreamClient.AudioPlayer();
Navigation = new StreamClient.Navigation({page: 'index', data: null});

