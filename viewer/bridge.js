import { App, applyDocumentTheme, applyHostStyleVariables } from '@modelcontextprotocol/ext-apps';

// Official SDK handles origin/session checks and the MCP Apps lifecycle.
const app = new App({name:'Arc-XRay',version:'0.1.0'}, {}, {autoResize:false});
app.ontoolresult = params => {
  const atlas = params._meta?.atlas || params.structuredContent?.atlas;
  if (atlas) window.ArcXRay.loadAtlas(atlas);
};
function hostStyle(context) {
  if (context?.theme) applyDocumentTheme(context.theme);
  if (context?.styles?.variables) applyHostStyleVariables(context.styles.variables);
  if (context?.safeAreaInsets) for (const [side,value] of Object.entries(context.safeAreaInsets))
    document.documentElement.style.setProperty('--safe-area-'+side, value+'px');
}
app.onhostcontextchanged = hostStyle;
window.addEventListener('arc-selection', event => {
  app.updateModelContext({structuredContent:event.detail}).catch(()=>{});
});
app.connect().then(()=>hostStyle(app.getHostContext())).catch(()=>window.ArcXRay.showHostError());
