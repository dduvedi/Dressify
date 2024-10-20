const { Client, Poll, MessageMedia } = require('whatsapp-web.js');
const qrcode = require('qrcode-terminal');

const client = new Client();

client.on('ready', () => {
    console.log('Client is ready!');
});

client.on('qr', qr => {
    qrcode.generate(qr, {small: true});
});

client.initialize();


client.on('message', async (msg) => {

    console.log('MESSAGE RECEIVED', msg);
    
if( msg.from.includes("9718229987") || msg.from.includes("8169602228") ) {
        if ( !msg.hasMedia && msg.body.includes("#style")) {
            
            // ######################################################################## //
            // ###### COMMAND - Text to Text recommendations with purchase links ###### //
            // ######################################################################## //

            console.log('MESSAGE RECEIVED FROM ', msg.from);    
            console.log('MESSAGE BODY ', msg.body);    
            
            
            // reply back "pong" directly to the message
            // msg.reply('Hi, Let’s make heads turn! What would you like to ask me today?');
            // msg.reply('Hi, Let’s make heads turn! ');

            // Make API request with the image data / textual data
            (async () => {
                const recommendations = await generateRecommendations(msg.body);
                console.log("Received recommendations:", recommendations);

                msg.reply('Here is my recommendation: \n ' + recommendations);
            })();

            
        }else if (msg.hasMedia && msg.body === "#wardrobe") {

            // ############################################# //
            // ###### COMMAND - Add Image to Wardrobe ###### //
            // ############################################# //

            const attachmentData = await msg.downloadMedia();
            // do something with the media data here
            // msg.reply('Hi, Let’s make heads turn! What would you like to ask me today?');
            console.log("Image received");

            /** msg.reply(`
                *Media info*
                MimeType: ${attachmentData.mimetype}
                Filename: ${attachmentData.filename}
                Data (length): ${attachmentData.data.length}
            `);**/

            // Make API request with the image data / textual data
            (async () => {
                const recommendations = await generateRecommendations(msg.body);
                console.log("Received recommendations:", recommendations);

                msg.reply('Here is my recommendation: \n ' + recommendations);
            })();

            // TEST Image Send
            // client.sendMessage(msg.from, attachmentData, { caption: 'Here\'s your requested media.' });

        }else if(!msg.hasMedia && (msg.body === "#1" || msg.body === "1") ){

            // ###################################################### //
            // ###### COMMAND - Steps To Add Image to Wardrobe ###### //
            // ###################################################### //

            const wa_wardrobe_msg = "👗 To Create Your Virtual Wardrobe 🪞\n\nSimply upload an image of your outfit with hastag *#wardrobe*";
            console.log(wa_wardrobe_msg);
            msg.reply(wa_wardrobe_msg);

        }else if(!msg.hasMedia && (msg.body === "#2" || msg.body === "2") ){

            // ############################################################## //
            // ###### COMMAND - Steps To Add Gen style recommendation ####### //
            // ############################################################## //

            const wa_style_msg = "🧥 To Generate a Style Recommendation 👗\n\nJust type #style and give me a bit more info:\n\n👤 About You:\n\nGender:\nAge:\nLocation:\nSkin Tone:\nBody Type:\n\n✨ Your Styling Preferences:\n\nOccasion (e.g., casual, formal, wedding):\nLook type (e.g., trendy, classic):\nFavorite colors:\nWeather:\n\nOnce you fill in these details and any other details of your choice, I’ll stitch together a stunning outfit just for you! 👗😎✨"
            console.log(wa_style_msg);
            msg.reply(wa_style_msg);
        }else if(!msg.hasMedia && (msg.body === "#3" || msg.body === "3")){

            // ############################################################## //
            // ###### COMMAND - Gen style recommendation from wardrobe ###### //
            // ############################################################## //

            const wa_style_from_wardrobe_msg = "3️⃣ To Generate an outfit from your wardrobe describe your styling requirements like occasion, look type, color preference, weather etc";
            console.log(wa_style_from_wardrobe_msg);
            msg.reply(wa_style_from_wardrobe_msg);
        }else{
            // msg.reply('Hi, Let’s make heads turn! What would you like to ask me today?');
            const wa_generic_msg = "Hi, Let’s make some heads turn! \n\n1️⃣ Create Your Virtual Wardrobe \n2️⃣ Get A Style Recommendation \n3️⃣ Use Your Existing Wardrobe For Recommendations \n\n Just reply with the number 1 or 2 or 3";

            console.log(wa_generic_msg);
            // msg.reply(wa_generic_msg);

            const media = MessageMedia.fromFilePath('./img/dressifai_icon.jpeg');
            await client.sendMessage(msg.from, media, { caption:  wa_generic_msg});

            // MYNTRA LINK 
            // msg.reply("https://www.myntra.com/bracelet/karishma+kreations/karishma-kreations-unisex-cubic-zirconia-gold-plated-kada-bracelet/29979855/buy");
        }


    
}

});

 async function generateRecommendations(userMsg){
    console.log("###### generateRecommendations ######");
    const url = 'https://cc97-14-143-179-90.ngrok-free.app/outfit/';
    const data = {
        prompt: "" + userMsg,
        imageString: ""
    };

    try {
        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data) // Convert the data to JSON string
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const apiData = await response.json(); // Parse the JSON response
        console.log('############### API Success:', apiData);
        console.log("############# recommendations =  = " + apiData?.choices[0]?.message?.content);

        return apiData?.choices[0]?.message?.content; // Return the data, if needed outside the function
    } catch (error) {
        console.error('############### Error:', error);
    }
}