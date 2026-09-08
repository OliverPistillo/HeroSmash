import{AssetManager}from'./engine/AssetManager.js';
import{Renderer}from'./engine/Renderer.js';
import{Input}from'./engine/Input.js';
import{SceneManager}from'./engine/SceneManager.js';
import{SaveSystem}from'./engine/SaveSystem.js';
import{AudioBus}from'./engine/Audio.js';
import{ParticleSystem}from'./engine/Particles.js';
import{AnimationSystem}from'./engine/AnimationSystem.js';
import{BootScene}from'./scenes/BootScene.js';
function mulberry32(seed){let a=seed>>>0;return()=>{a+=0x6D2B79F5;let t=a;t=Math.imul(t^t>>>15,t|1);t^=t+Math.imul(t^t>>>7,t|61);return((t^t>>>14)>>>0)/4294967296}}
const canvas=document.getElementById('game'),renderer=new Renderer(canvas),save=new SaveSystem(),app={canvas,renderer,assets:new AssetManager(),input:null,scenes:null,save,audio:new AudioBus(),particles:new ParticleSystem(),anim:new AnimationSystem(),state:null,rng:mulberry32(Date.now()),speed:1};
app.input=new Input(canvas,renderer);app.scenes=new SceneManager(app);app.scenes.set(BootScene);let last=performance.now();function frame(now){let dt=Math.min(.05,(now-last)/1000);last=now;app.scenes.handleInput(app.input.consume());app.scenes.update(dt);renderer.begin();app.scenes.draw(renderer);renderer.end();requestAnimationFrame(frame)}requestAnimationFrame(frame);
