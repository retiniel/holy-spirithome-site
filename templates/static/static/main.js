// Quick anchors
document.getElementById("openPrayer").addEventListener("click", function(){
  location.hash = "#prayer";
  document.getElementById("prayer_subject").focus();
});
document.getElementById("openContact").addEventListener("click", function(){
  location.hash = "#contact";
  document.getElementById("contact_message").focus();
});

async function postJson(url, data){
  const res = await fetch(url, {
    method: "POST",
    headers: {"Content-Type":"application/json"},
    body: JSON.stringify(data)
  });
  const json = await res.json().catch(()=>({ok:false, msg:"Réponse serveur invalide"}));
  return json;
}

document.getElementById("sendPrayer").addEventListener("click", async function(){
  const name = document.getElementById("prayer_name").value;
  const email = document.getElementById("prayer_email").value;
  const subject = document.getElementById("prayer_subject").value;
  const details = document.getElementById("prayer_details").value;
  const msgEl = document.getElementById("prayerMsg");
  msgEl.textContent = "Envoi...";
  try{
    const res = await postJson("/submit_prayer", {name, email, subject, details});
    msgEl.textContent = res.msg || "OK";
    if(res.ok) document.getElementById("prayerForm").reset();
  } catch(err){
    msgEl.textContent = "Erreur réseau: " + err;
  }
});

document.getElementById("sendContact").addEventListener("click", async function(){
  const name = document.getElementById("contact_name").value;
  const email = document.getElementById("contact_email").value;
  const message = document.getElementById("contact_message").value;
  const msgEl = document.getElementById("contactMsg");
  msgEl.textContent = "Envoi...";
  try{
    const res = await postJson("/contact", {name, email, message});
    msgEl.textContent = res.msg || "OK";
    if(res.ok) document.getElementById("contactForm").reset();
  } catch(err){
    msgEl.textContent = "Erreur réseau: " + err;
  }
});
