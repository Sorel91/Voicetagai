// Optional browser-provided live speech recognition.
// This is NOT Whisper and may send speech to the browser vendor's service.
(function(){
 const root=document.getElementById('browserTranscription');
 if(!root)return;
 const SR=window.SpeechRecognition||window.webkitSpeechRecognition;
 const button=document.getElementById('liveTranscriptButton');
 const status=document.getElementById('liveTranscriptStatus');
 const preview=document.getElementById('liveTranscriptPreview');
 if(!SR){button.disabled=true;status.textContent='Reconnaissance vocale en direct non prise en charge par ce navigateur. Le moteur serveur est en préparation.';return}
 let recognition=null,enabled=false,starting=false;
 const create=()=>{const r=new SR();r.lang='fr-FR';r.continuous=true;r.interimResults=true;
 r.onresult=(event)=>{let interim='';for(let i=event.resultIndex;i<event.results.length;i++){const result=event.results[i];const phrase=result[0].transcript.trim();if(result.isFinal){if(phrase&&typeof window.voicetagAddNote==='function')window.voicetagAddNote(phrase,window.voicetagCurrentSpeaker?.()||'Non attribué')}else interim+=phrase+' '}preview.textContent=interim?'En cours : '+interim:''};
 r.onerror=(e)=>{status.textContent='Reconnaissance vocale : '+e.error+'. Réessaie ou utilise les notes manuelles.';if(['not-allowed','service-not-allowed','audio-capture'].includes(e.error)){enabled=false;button.textContent='Activer la transcription en direct'}};
 r.onend=()=>{starting=false;if(enabled){try{starting=true;r.start()}catch(e){enabled=false;starting=false;status.textContent='La reconnaissance vocale s’est interrompue : '+e.message;button.textContent='Activer la transcription en direct'}}else{button.textContent='Activer la transcription en direct'}};
 return r};
 button.onclick=()=>{if(enabled){enabled=false;button.textContent='Activer la transcription en direct';status.textContent='Transcription en direct arrêtée.';preview.textContent='';try{recognition?.stop()}catch(e){}return}enabled=true;recognition=create();try{recognition.start();starting=true;button.textContent='Arrêter la transcription en direct';status.textContent='Écoute en cours via le service de reconnaissance du navigateur. Les phrases finalisées sont ajoutées à la chronologie.'}catch(e){enabled=false;button.textContent='Activer la transcription en direct';status.textContent='Impossible de démarrer : '+e.message}};
 window.addEventListener('pagehide',()=>{enabled=false;try{recognition?.stop()}catch(e){}});
})();
