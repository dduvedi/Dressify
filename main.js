const { Client, Poll, MessageMedia } = require('whatsapp-web.js');
const qrcode = require('qrcode-terminal');

const ffmpeg = require('fluent-ffmpeg');
const ffmpegPath = require('ffmpeg-static'); // Automatically resolves the path to ffmpeg
const path = require('path');

// Explicitly tell fluent-ffmpeg where to find ffmpeg
ffmpeg.setFfmpegPath(ffmpegPath);  // This sets the correct ffmpeg path

const FormData = require('form-data');


const client = new Client();
const fs = require('fs');

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

                msg.reply('Here is my recommendation: \n ' + recommendations?.recommendations);

                const meta_data = recommendations?.meta_data;
                console.log("meta_data = " + meta_data);

                const meta_data_results_0 = meta_data.results[0].products[0].product_url;
                console.log("meta_data_results = " + meta_data_results_0);

                const meta_data_results_1 = meta_data.results[1].products[0].product_url;
                console.log("meta_data_results = " + meta_data_results_1);


                // Add URLs here    
                msg.reply(meta_data_results_0);

                msg.reply(meta_data_results_1);
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

        }else if (msg.hasMedia) {

            // ############################################# //
            // ###### COMMAND - Audio to text to recommendation ###### //
            // ############################################# //

            const attachmentData = await msg.downloadMedia();
            // do something with the media data here
            // msg.reply('Hi, Let’s make heads turn! What would you like to ask me today?');
            console.log("Media received");

            msg.reply(`
                *Media info*
                MimeType: ${attachmentData.mimetype}
                Filename: ${attachmentData.filename}
                Data (length): ${attachmentData.data.length}
            `);

            // Download the WA audio

            fs.writeFile(
                "./dl/" + attachmentData.filename + ".ogg",
                attachmentData.data,
                "base64",
                function (err) {
                    if (err) {
                      console.log(err);
                    }
                }
            );

            // ENDS: Download the WA audio
            

            // ###### Convert ogg to wav for Sargam AI
            const inputOgg = "./dl/" + attachmentData.filename + ".ogg"; // Provide your .ogg file path
            const outputWav = "./dl/converted/" + attachmentData.filename + ".wav" // Desired .wav file output path
            convertOggToWav(inputOgg, outputWav)
              .then((outputFilePath) => {
                console.log(`File has been converted to: ${outputFilePath}`);
              })
              .catch((err) => {
                console.error('Error occurred during conversion:', err);
              });

            // ###### ENDS: Convert ogg to wav for Sargam AI

            // ###### MAKE SARGAM API CALL TO GET AUDIO TO TEXT
            const filePath = "./dl/converted/" + attachmentData.filename + ".wav";
            console.log("File Path: ", filePath);
            console.log("File Exists: ", fs.existsSync(filePath));


            const form = new FormData();
            // form.append('my_buffer', new Buffer(10));
            form.append('file', fs.readFileSync("./dl/converted/" + attachmentData.filename + ".wav"));
            form.append("model", "saaras:v1");

            const options = {
              method: 'POST',
              headers: {
                'api-subscription-key': '7c6727166'
              
              },
              body: form // Set form as the request body

            };

            // options.body = form;

            fetch('https://api.sarvam.ai/speech-to-text-translate', options)
              .then(response => response.json())
              .then(response => console.log("VOICE TO TEXT response = " + JSON.stringify(response) ))
              .catch(err => console.error(err));

            // ###### ENDS: MAKE SARGAM API CALL TO GET AUDIO TO TEXT

            // Make API request with the image data / textual data
            /** (async () => {
                const recommendations = await generateRecommendations(msg.body);
                console.log("Received recommendations:", recommendations);

                msg.reply('Here is my recommendation: \n ' + recommendations);
            })(); **/

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
        console.log("############# recommendations =  = " + apiData?.response?.choices[0]?.message?.content);
        console.log("############# meta_data =  = " + apiData?.metaData);

        const metaDataAndReco = {"recommendations":apiData?.response?.choices[0]?.message?.content, "meta_data": JSON.parse(apiData?.metaData) }

        // return apiData?.response?.choices[0]?.message?.content; // Return the data, if needed outside the function
        return metaDataAndReco;

    } catch (error) {
        console.error('############### Error:', error);
    }
}


// Function to convert ogg to wav
function convertOggToWav(inputFilePath, outputFilePath) {
  return new Promise((resolve, reject) => {
    ffmpeg(inputFilePath)
      .toFormat('wav')
      .on('end', () => {
        console.log('Conversion finished successfully.');
        resolve(outputFilePath);
      })
      .on('error', (err) => {
        console.error('Error during conversion:', err);
        reject(err);
      })
      .save(outputFilePath);
  });
}