window.Streamserver = {};
////////////////////////
//Class Playlist////////
////////////////////////
Streamserver.Playlist = function(){
this.playlistTag=$("#playlist");

}

Streamserver.Playlist.prototype.Update=function(data)
{
	var table=$("<table>").attr("class","table table-striped");
	for (var r = 0; r < data.length ; r++) {
		var row = $("<tr>");
		$("<td>").text(data[r].id).appendTo(row);
		var a=$("<a>").attr("href",data[r].href).text(data[r].name);
		var td=$("<td>"); a.appendTo(td); td.appendTo(row);
		$("<td>").text(data[r].size).appendTo(row);
		row.appendTo(table);
	}
	this.playlisttag.html(table);
}

Streamserver.Playlist.prototype.SetHeight=function(){
	playerHeight=$('footer').height();
	this.playlistTag.height(window.innerHeight-playerHeight-100);
	this.playlistTag.css("overflow", "auto");
}


///////////////////////////
//Class Slider/////////////
///////////////////////////
Streamserver.Slider=function()
{
$('#labelslider').slider();
this.sliderTag=$('#slider').children().width(window.innerWidth);
}


///////////////////////////
//Class Player////////
///////////////////////////
Streamserver.Player=function(url)
{
this.context="undefined";
if (typeof AudioContext !== "undefined") {
    this.context = new AudioContext();
} else if (typeof webkitAudioContext !== "undefined") {
    this.context = new webkitAudioContext();
} else {
    throw new Error('AudioContext not supported. :(');
}

// переменные для буфера, источника и получателя
this.buffer="undefined"; 
this.source="undefined"; 
this.destination="undefined";
this.loadSoundFile(url);
}
// функция для подгрузки файла в буфер
Streamserver.Player.prototype.loadSoundFile = function(url) {
  // делаем XMLHttpRequest (AJAX) на сервер
  var xhr = new XMLHttpRequest();
  xhr.open('GET', url, true);
  xhr.responseType = 'arraybuffer'; // важно
  xhr.onload = function(e) {
    // декодируем бинарный ответ
    Player.context.decodeAudioData(xhr.response,
    function(decodedArrayBuffer) {
      // получаем декодированный буфер
      Player.buffer = decodedArrayBuffer;
    }, function(e) {
      console.log('Error decoding file', e);
    });
  };
  xhr.send();
}

// функция начала воспроизведения
Streamserver.Player.prototype.play = function(){
  // создаем источник
  this.source = this.context.createBufferSource();
  // подключаем буфер к источнику
  this.source.buffer = this.buffer;
  // дефолтный получатель звука
  this.destination = this.context.destination;
  // подключаем источник к получателю
  this.source.connect(destination);
  // воспроизводим
  this.source.start(0);
}

// функция остановки воспроизведения
Streamserver.Player.prototype.stop = function(){
  this.source.stop(0);
}


////////////////////////////////
//User Interface Events/////////
////////////////////////////////

//"Random" click:
$("#random").click(function(){
$.getJSON($SCRIPT_ROOT + '/_preload', {
        start:1,
        count: 20
      }, function(data) {
        Playlist.Update(data.data);
      });
      return false;
});

var Playlist=new Streamserver.Playlist();

//Preloading playlist on scroll
Playlist.playlistTag.scroll(function(e){
    var scrollAmount = Playlist.playlistTag.scrollTop();
    var documentHeight = Playlist.playlistTag.children().height();
    var scrollPercent = (scrollAmount / documentHeight) * 100;
    if(scrollPercent > 50) 
	{
		preloadAnotherData(); 
	}
});
var  preloadAnotherData=function() 
{ 
//TODO: write me
}




//here goes visuals


//create slider


//here we go, lets start:

var Player=new Streamserver.Player('/getmedia/75.mp3');
var Slider=new Streamserver.Slider();
Playlist.SetHeight();
//loadSoundFile('/getmedia/75.mp3');
setTimeout(Player.play, 4000);