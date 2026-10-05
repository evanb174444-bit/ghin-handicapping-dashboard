function compositionDonut(title,tone,items,colors) {
  const total=items.reduce((n,item)=>n+item[1],0),labels=[];
  let angle=-90;
  const point=(radius,a)=>[50+radius*Math.cos(a*Math.PI/180),50+radius*Math.sin(a*Math.PI/180)].join(',');
  const slices=items.map((item,i)=>{
    const share=total?item[1]/total:0,sweep=share*360,start=angle,end=start+sweep,mid=start+sweep/2;
    angle=end;
    if(!share)return '';
    let path;
    if(share>=1-1e-12){
      path='M50,0 A50,50 0 1 1 50,100 A50,50 0 1 1 50,0 M50,30 A20,20 0 1 0 50,70 A20,20 0 1 0 50,30';
    }else{
      path=`M${point(50,start)} A50,50 0 ${sweep>180?1:0} 1 ${point(50,end)} L${point(20,end)} A20,20 0 ${sweep>180?1:0} 0 ${point(20,start)} Z`;
    }
    if(share>=.04){const x=50+35*Math.cos(mid*Math.PI/180),y=50+35*Math.sin(mid*Math.PI/180);labels.push(`<text class="composition-donut-ring-label" x="${x}" y="${y-1.7}"><tspan class="composition-donut-ring-name" x="${x}">${esc(item[0])}</tspan><tspan class="composition-donut-ring-value" x="${x}" dy="5.2">${pct(share)}</tspan></text>`)}
    return `<path class="donut-slice composition-donut-sector" d="${path}" fill="${colors[i]}" fill-rule="evenodd" data-category="${esc(item[0])}" data-count="${fmt(item[1])}" data-share="${pct(share)}" tabindex="0" aria-label="${esc(item[0])}: ${fmt(item[1])}, ${pct(share)}"/>`;
  }).join('');
  return `<article class="composition-card ${tone}"><div class="composition-band">${title}</div><div class="composition-body composition-donut-layout"><div class="composition-donut-wrap"><svg class="composition-donut-svg" viewBox="0 0 100 100" role="img" aria-label="${esc(title)} composition donut">${slices}${labels.join('')}</svg><div class="composition-donut-total"><strong>${short(total)}</strong><span>Total</span></div></div></div></article>`;
}
