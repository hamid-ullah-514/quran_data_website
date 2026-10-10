function openSurah(){
    const number=document.getElementById("surahNumber").value;

    if(number){
        window.location.href="/surah/"+number;
    }
}

async function addFavorite(surah,ayah){
    const note=prompt("اس آیت کے لیے اپنا Note لکھیں:");

    if(note===null){
        return;
    }

    const response=await fetch("/api/favorites",{
        method:"POST",
        headers:{
            "Content-Type":"application/json"
        },
        body:JSON.stringify({
            surah_number:surah,
            ayah_number:ayah,
            note:note
        })
    });

    const data=await response.json();

    alert(data.message);
}

async function updateFavorite(id){
    const newNote=prompt("نیا Note لکھیں:");

    if(newNote===null || newNote.trim()===""){
        return;
    }

    const response=await fetch("/api/favorites/"+id,{
        method:"PUT",
        headers:{
            "Content-Type":"application/json"
        },
        body:JSON.stringify({
            note:newNote
        })
    });

    const data=await response.json();

    alert(data.message);

    location.reload();
}

async function deleteFavorite(id){
    const confirmDelete=confirm(
        "کیا آپ واقعی اس Favorite کو Delete کرنا چاہتے ہیں؟"
    );

    if(!confirmDelete){
        return;
    }

    const response=await fetch("/api/favorites/"+id,{
        method:"DELETE"
    });

    const data=await response.json();

    alert(data.message);

    location.reload();
}