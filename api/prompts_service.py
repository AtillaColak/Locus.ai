import openai
import asyncio
import requests

# Set the OpenAI API key, set env
openai.api_key = "your_api_key"


def generate_response(form_data):
    completions = openai.Completion.create(
        engine="text-davinci-002",
        prompt= f"Please generate a detailed list of all the objects, scenes, "
                f"and persons mentioned in the following story. "
                f"Your list should include specific descriptions of each item, "
                f"and each item should be separated with a dash (-) for clarity."
                f" The story is provided here, "
                f"[lease use your knowledge and creativity to provide a comprehensive and engaging list: {form_data}",
        max_tokens=1024,
        n=1,
        stop=None,
        temperature=0.8,
    )
    message = completions.choices[0].text
    return message.strip()

async def query_async(payload, headers):
    API_URL = "https://api-inference.huggingface.co/models/prompthero/openjourney"
    response = requests.post(API_URL, headers=headers, json=payload)
    if(response.status_code == 503):
        return "The system is currently under maintenance. Please try again later."
    return response.content

def format_object(item, design):
    design_image = ""
    if(design == "DnD Style"):
        design_image = f"mdjrny-v4 style, A photorealistic concept art like a dungeons and dragons {item}. " \
                       "d&d, highly detailed, highly detailed fantasy, cinematic, realistic, " \
                       "full body, concept art, highly detailed face, character design, cinematic" \
                       "character concept comic book cover, high quality, by rutkowski" \
                       "by William O'Connor, Larry Elmore, Justin Gerrard" \
                       ", trending art, Trending on Artstation."
    elif(design == "comic"):
        design_image = f"mdjrny-v4 style, retro comic style artwork, highly detailed {item}, comic book," \
                       f"symmetrical, high quality, detailed face, vibrant, comic book cover, peter mohrbacher."
    elif(design == "3d art"):
        design_image = f"mdjrny-v4 style, very very cute disney pixar {item}, smooth lighting, soft smooth pastel colors" \
                       f" ultra detailed," \
                       f" depth of field, " \
                       f"vibrant details, hyperrealistic, unreal engine, unreal 5, daz, " \
                       f"high quality, 8k, pop surrealism, modern disney style, pixar style, square image"
    elif(design == "Hyperrealist"):
        design_image = f"display {item} with perfect composition, hyperrealistic, high quality," \
                       f" mdjrny-v4 style,insanely detailed and intricate, octane render, unreal engine, 8k, " \
                       f"by greg rutkowski and Peter Mohrbacher and magali villeneuve" \
                       f" trending art" \
                       f"trending on artstation, sharp focus"

    return design_image


def generate_images(form_data, design):
    list_items = generate_response(form_data)
    items_list = list_items.split('\n')
    starting_with_dash = [item[1:] for item in items_list if item.startswith('-')]
    if len(starting_with_dash) == 0:
        return -1

    images = []

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    futures = []

    headers = {"Authorization": f"Bearer your_SD_key"}

    for item in starting_with_dash:
        future = asyncio.ensure_future(query_async({
            "inputs": format_object(item, design),
        }, headers))
        futures.append(future)

    while futures:
        done, futures = loop.run_until_complete(asyncio.wait(futures))
        for future in done:
            image_bytes = future.result()
            if isinstance(image_bytes, str) and "The system is currently under maintenance." in image_bytes:
                continue
            if image_bytes is not None:
                images.append(image_bytes)

    loop.close()
    if len(images) == 0:
        images_error = []
        images_error.append("The system is currently under maintenance.")
        return images_error

    return images
