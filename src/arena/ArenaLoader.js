export async function loadJson(url) {
  const res = await fetch(url);
  if (!res.ok) throw new Error(`Failed to load JSON: ${url}`);
  return await res.json();
}

export async function loadImage(url) {
  return await new Promise((resolve, reject) => {
    const img = new Image();
    img.onload = () => resolve(img);
    img.onerror = () => reject(new Error(`Failed to load image: ${url}`));
    img.src = url;
  });
}

export async function loadArena(configUrl) {
  const config = await loadJson(configUrl);
  const images = new Map();
  const layers = config.layers || [];
  await Promise.all(layers
    .filter(layer => layer.asset)
    .map(async layer => images.set(layer.asset, await loadImage(layer.asset))));
  return { config, images };
}
