function startConverting(lang)
{              
  document.getElementById("speakBtn").style.visibility = "hidden";   
  var r=document.getElementById('searchBox');
  var SpeechRecognition = SpeechRecognition || webkitSpeechRecognition || null;
  const recognition = new SpeechRecognition();
  //var recognition=new webkitSpeechRecognition(); //Initialisation of web Kit
  recognition.continuous=false; //True if continous conversion is needed, false to stop transalation when paused 
  recognition.interimResults=true;
  //recognition.lang=lang; //'en-US'
  //recognition.lang = 'ja-JP';
  recognition.start();
  var ftr='';
  recognition.onresult=function(event){
      var interimTranscripts='';
      for(var i=event.resultIndex;i<event.results.length;i++)
      {
          var transcript=event.results[i][0].transcript;
          transcript.replace("\n"," ")
          if(event.results[i].isFinal){
              ftr+=transcript;
          }
          else
          interimTranscripts+=transcript;
      }
      r.setAttribute('value',ftr +interimTranscripts) ;
  };
  recognition.onspeechend = function() {
    recognition.stop();
    document.getElementById("speakBtn").style.visibility = "visible";   
    console.log('Speech recognition has stopped.');
  }
    recognition.onerror=function(event){};
}