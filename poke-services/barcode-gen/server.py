#!/usr/bin/env python3
"""Barcode Generator — Code39, Code128-B, EAN-13. Port: 8782. Pure Python."""
import http.server, json, urllib.parse, os

PORT = int(os.environ.get("PORT", 8782))
FREE_LIMIT = 5
ip_usage = {}

CODE39 = {
    '0':'101001101101','1':'110100101011','2':'101100101011','3':'110110010101',
    '4':'101001101011','5':'110100110101','6':'101100110101','7':'101001011011',
    '8':'110100101101','9':'101100101101','A':'110101001011','B':'101101001011',
    'C':'110110100101','D':'101011001011','E':'110101100101','F':'101101100101',
    'G':'101010011011','H':'110101001101','I':'101101001101','J':'101011001101',
    'K':'110101010011','L':'101101010011','M':'110110101001','N':'101011010011',
    'O':'110101101001','P':'101101101001','Q':'101010110011','R':'110101011001',
    'S':'101101011001','T':'101011011001','U':'110010101011','V':'100110101011',
    'W':'110011010101','X':'100101101011','Y':'110010110101','Z':'100110110101',
    '-':'100101011011','.':'110010101101',' ':'100110101101','$':'100100100101',
    '/':'100100101001','+':'100101001001','%':'101001001001','*':'100101101101',
}
C39_STARTER = '100101101101'

def enc39(t):
    t=t.upper()
    for c in t:
        if c not in CODE39: return None,f"Bad char '{c}' for Code39"
    b=C39_STARTER+'0'
    for c in t: b+=CODE39[c]+'0'
    return b+C39_STARTER,None

C128P=[
    '11011001100','11001101100','11001100110','10010011000','10010001100',
    '10001001100','10011001000','10011000100','10001100100','11001001000',
    '11001000100','11000100100','10110011100','10011011100','10011001110',
    '10111001100','10011101100','10011100110','11001110010','11001011100',
    '11001001110','11011100100','11001110100','11101101110','11101001100',
    '11100101100','11100100110','11101100100','11100110100','11100110010',
    '11011011000','11011000110','11000110110','10100011000','10001011000',
    '10001000110','10110001000','10001101000','10001100010','11010001000',
    '11000101000','11000100010','10110111000','10110001110','10001101110',
    '10111011000','10111000110','10001110110','11101110110','11010001110',
    '11000101110','11011101000','11011100010','11011101110','11101011000',
    '11101000110','11100010110','11101101000','11101100010','11100011010',
    '11101111010','11001000010','11110001010','10100110000','10100001100',
    '10010110000','10010000110','10000101100','10000100110','10110010000',
    '10110000100','10011010000','10011000010','10000110100','10000110010',
    '11000010010','11001010000','11110111010','11000010100','10001111010',
    '10100111100','10010111100','10010011110','10111100100','10011110100',
    '10011110010','11110100100','11110010100','11110010010','11011011110',
    '11011110110','11110110110','10101111000','10100011110','10001011110',
    '10111101000','10111100010','11110101000','11110100010','10111011110',
    '10111101110','11101011110','11110101110','11010000100','11010010000',
    '11010011100','11000111010',
]

def enc128(t):
    codes=[104]
    for c in t:
        if 32<=ord(c)<=127: codes.append(ord(c)-32)
        else: return None,f"Bad char '{c}' for Code128"
    ck=codes[0]
    for i,c in enumerate(codes[1:],1): ck+=c*i
    codes.append(ck%103); codes.append(106)
    b=''.join(C128P[c] for c in codes)
    return b+'11',None

EAN_LO=['0001101','0011001','0010011','0111101','0100011','0110001','0101111','0111011','0110111','0001011']
EAN_LE=['0100111','0110011','0011011','0100001','0011101','0111001','0000101','0010001','0001001','0010111']
EAN_R=['1110010','1100110','1101100','1000010','1011100','1001110','1010000','1000100','1001000','1110100']
EAN_PAR=['LLLLLL','LLGLGG','LLGGLG','LLGGGL','LGLLGG','LGGLLG','LGGGLL','LGLGLG','LGLGGL','LGGLGL']

def encean(t):
    if len(t)<12 or len(t)>13: return None,"Need 12-13 digits"
    if not t[:12].isdigit(): return None,"Digits only"
    if len(t)==12:
        s=sum(int(t[i])*(1 if i%2==0 else 3) for i in range(12))
        t=t+str((10-s%10)%10)
    p=EAN_PAR[int(t[0])]
    b='101'
    for i,ch in enumerate(p):
        b+=EAN_LO[int(t[i+1])] if ch=='L' else EAN_LE[int(t[i+1])]
    b+='01010'
    for i in range(6): b+=EAN_R[int(t[i+7])]
    return b+'101',None

def to_svg(bars,txt='',h=80,mw=2):
    if not bars: return ''
    tw=len(bars)*mw; w=max(tw+20,60); h2=h+(30 if txt else 0)
    r=''.join(f'<rect x="{10+i*mw}" y="10" width="{mw}" height="{h}" fill="black"/>' for i,b in enumerate(bars) if b=='1')
    l=f'<text x="{w//2}" y="{h2-8}" text-anchor="middle" font-family="monospace" font-size="12">{txt}</text>' if txt else ''
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h2}">{r}{l}</svg>'

class H(http.server.BaseHTTPRequestHandler):
    def log_message(self,*a): pass
    def do_GET(self):
        p=urllib.parse.urlparse(self.path)
        if p.path=='/api/health': self._r(200,{'ok':True,'service':'barcode','v':1,'formats':['code39','code128','ean13']})
        elif p.path=='/api/usage': self._r(200,{'used':ip_usage.get(self.client_address[0],0),'limit':FREE_LIMIT})
        elif p.path=='/api/generate':
            q=urllib.parse.parse_qs(p.query)
            d=q.get('data',[''])[0]; f=q.get('format',['code128'])[0].lower()
            o=q.get('output',['svg'])[0]; h=int(q.get('height',[80])[0])
            mw=int(q.get('width',[2])[0])
            if not d: self._r(400,{'error':"missing 'data'"}); return
            ip=self.client_address[0]
            if ip_usage.get(ip,0)>=FREE_LIMIT: self._r(402,{'error':'free limit exceeded','wallet':'0xca3d86e4EDE205E6d72496BC2919c88b994B6beF','chain':'base'}); return
            ip_usage[ip]=ip_usage.get(ip,0)+1
            enc={'code39':enc39,'code128':enc128,'ean13':encean}
            if f not in enc: self._r(400,{'error':f'bad format. Use: {list(enc.keys())}'}); return
            bars,err=enc[f](d)
            if err: self._r(400,{'error':err}); return
            if o=='svg':
                self.send_response(200); self.send_header('Content-Type','image/svg+xml')
                self.send_header('Access-Control-Allow-Origin','*'); self.end_headers()
                self.wfile.write(to_svg(bars,d,h,mw).encode())
            else: self._r(200,{'format':f,'data':d,'modules':len(bars)})
        else: self._r(404,{'error':'not found'})
    def _r(self,s,b):
        self.send_response(s); self.send_header('Content-Type','application/json')
        self.send_header('Access-Control-Allow-Origin','*'); self.end_headers()
        self.wfile.write(json.dumps(b).encode())

if __name__=='__main__':
    s=http.server.HTTPServer(('0.0.0.0',PORT),H)
    print(f'Barcode Generator on port {PORT}'); s.serve_forever()
