/** 
桌面虎鲸
Author: hai321
参考资料：
[源码分享] HTMLayout 使用APNG制作桌面透明动画窗口 
http://bbs.aardio.com/thread-7922-1-1.html
**/

import win.ui;
import winex;
/*DSG{{*/
winform = ..win.form( text="虎鲸";bottom=170;parent=...;right=297;border="none";topmost=1;exmode="toolwindow";mode="popup";cls="hujing" )
winform.add(  )
/*}}*/

//启用分层窗口以支持桌面透明
winform.transparent(true);

import web.layout;
wbLayout = web.layout(winform);


wbLayout.html =/***
<div id="myTab"><img src="/res/daddy-left.png"/></div>
<menu.context id="menuId">
  <li>桌面图标
     <menu>
                  <li id="i1">隐藏图标</li>
                  <li id="i2">显示图标</li>
     </menu>  
  </li> 
  <li>选择鲸鱼
     <menu>
     <li id="i5">鲸鱼爸爸</li>
     <li id="i6">鲸鱼妈妈</li>
     <li id="i6">鲸鱼宝宝</li>
     </menu>  
  </li>
   <li id="i7">关于虎鲸</li>
   <li id="i8">退出</li>
</menu>  
***/


wbLayout.css = /**
html {   
    background-color:transparent; /*网页背景透明*/
    context-menu:selector(menu#menuId);
} 
menu{
          width: max-intrinsic; /*内容的最大宽度,可以超出屏幕*/      
          background: url(/res/menu-back-office.png) expand;
          background-position: 0 0 0 24;
          text-align:left;
} 
**/ 

//修改节点代码
xghtml=function(){
        if( thread.get("我是") = "爸爸"){
              var myTab = wbLayout.getEle("myTab")//获取节点
               if(myTab){
                       if(向左游动 = false){
                               myTab.child(1).innerHTML = '<img src="/res/daddy-right.png" />'
                       }else {
                               myTab.child(1).innerHTML = '<img src="/res/daddy-left.png" />'
                       }         
               }
    }        
        elseif( thread.get("我是") = "妈妈"){
              var myTab = wbLayout.getEle("myTab")//获取节点
               if(myTab){
                       if(向左游动 = false){
                               myTab.child(1).innerHTML = '<img src="/res/mummy-right.png" />'
                       }else {
                               myTab.child(1).innerHTML = '<img src="/res/mummy-left.png" />'
                       }         
               }
    }
        elseif( thread.get("我是") = "宝宝"){
              var myTab = wbLayout.getEle("myTab")//获取节点
               if(myTab){
                       if(向左游动 = false){
                               myTab.child(1).innerHTML = '<img src="/res/son-right.png" />'
                       }else {
                               myTab.child(1).innerHTML = '<img src="/res/son-left.png" />'
                       }         
               }
    }
    是否游动 = true; 
        winform.changeInterval(tmid,15);//修改定时器
}

wbLayout.documentElement.attachEventHandler(
    //鼠标按下拖动触发下面的函数
    onMouseMove = function (ltTarget,ltEle,x,y,ltMouseParams) {
        if( ltMouseParams.button_state == 1/*_HL_MAIN_MOUSE_BUTTON*/ ){
                是否游动 = false;  
                winform.changeInterval(tmid,5000) 
            var wx,wy = winform.getPos();
            wx = wx + (x - winform.downPos.x)
            wy = wy + (y - winform.downPos.y)
            ltTarget.getForm().setPos( wx,wy)
            return true;
        }  
    }     
    //鼠标按下触发下面的函数
    onMouseDown = function (ltTarget,ltEle,x,y,ltMouseParams) {
              if( ltMouseParams.button_state == 1/*_HL_MAIN_MOUSE_BUTTON*/ ){ 
                      是否游动 = false                 
                    winform.changeInterval(tmid,1000000)        //定时器暂停3秒等待退出等命令
                       winform.capture = true;
                      winform.downPos = { x = x ;y = y}                 
        } 
        elseif(ltMouseParams.button_state==2){ 
                是否游动 = false                    
                    winform.changeInterval(tmid,1000000)        //定时器暂停3秒等待退出等命令
                       winform.capture = true;
                      winform.downPos = { x = x ;y = y}                
        }                      
    }
    //鼠标弹起触发下面的函数
    onMouseUp = function (ltTarget,ltEle,x,y,ltMouseParams) {              
            if( ltMouseParams.button_state == 1/*_HL_MAIN_MOUSE_BUTTON*/ ){
                    winform.changeInterval(tmid,15);//修改定时器
                         是否游动 = true;                          
        } 
    }
) 

//桌面句柄
var hDskManager,hShellView = winex.findExists("",,"<Progman>|<WorkerW>","SHELLDLL_DefView") 

//右键菜单触发下面的函数
wbLayout.onMenuItemClick = function (ltTarget,ltEle,reason,behaviorParams) {
        是否游动 = false;   
   if( ltTarget.innerText == "退出" ){   
              if(hShellView)win.show(hShellView,true);//退出前显示桌面图标                  
       winform.close();
   } 
   elseif(ltTarget.innerText == "隐藏图标"){
                   win.show(hShellView,false);//隐藏桌面图标
                   winform.changeInterval(tmid,15);//修改定时器
                    是否游动 = true;
   }
   elseif(ltTarget.innerText == "显示图标"){
                   win.show(hShellView,true);//显示桌面图标
                   winform.changeInterval(tmid,15);//修改定时器
                    是否游动 = true;
   }  
   elseif( ltTarget.innerText == "鲸鱼爸爸" ){ 
                     thread.set("我是","爸爸" ) 
                     xghtml();//修改代码                     
   } 
   elseif( ltTarget.innerText == "鲸鱼妈妈" ){ 
                     thread.set("我是","妈妈" ) 
                     xghtml();//修改代码                     
   } 
   elseif( ltTarget.innerText == "鲸鱼宝宝" ){ 
                     thread.set("我是","宝宝" ) 
                     xghtml();//修改代码
   } 
   elseif( ltTarget.innerText == "关于虎鲸" ){ 
                import process
                process.execute("http://baike.baidu.com/view/9005.htm")        
                winform.changeInterval(tmid,15);//修改定时器
                   是否游动 = true;
   }    
}

//默认设置
横位置,纵位置 = win.getScreen();//取系统分辨率
var hwnd = winform.hwnd; 
win.setPos(hwnd,横位置-200,200);//起始位置
winform.show() 
math.randomize()
num = 1; 
r = 0;
thread.set("我是","爸爸" ) 
向左游动 = true; //向左移动
是否游动 = true; //开始时游动

//随机向上向下平行游动
randmove=function(tmid,xnum){                                                                                  
        if(num>200 and cy<纵位置 and cy>0 ){//在屏幕内游动200次后，随机改变方向
                r = math.random(-1,1);
                num = 1;
        }
        elseif(cy>纵位置+20){//游动超出屏幕下方时改为向上游动
                r=-1
        }
        elseif(cy<-20){//游动超出屏幕上方时改为向下游动
                r=1
        }
         num =num+ 1;                                          
         if(r=0){//直线游动时减慢速度
                 winform.changeInterval(tmid,25)                                                 
         }
         else{//加快速度
                 winform.changeInterval(tmid,15)
         }                                         
        win.setPos(hwnd,cx+xnum,cy+r)        
}

//向左移动
left=function(tmid){
    cx,cy = win.getPos(hwnd,true)                
        if(cx>-240){//未超出屏幕左边时，随机游动
                xnum=-1
                randmove(tmid,xnum)//随机游动
        }                                
        else {                        
                向左游动 = false;;//调用向右移动;
                xghtml();//修改代码        
        }        
}

//向右移动
right=function(tmid){
    cx,cy = win.getPos(hwnd,true)                                
        if(cx<横位置){//未超出屏幕右边时，随机游动
                xnum=1
                randmove(tmid2,xnum);//随机游动
        }
        else {                
                向左游动 = true; ;//向左移动                                        
                xghtml();//修改代码        
        } 
}

//定时器控制游动
tmid = winform.setInterval(
    15/*毫秒*/,
    function(hwnd,msg,id,tick){                
            if(是否游动 = true){  
                if(向左游动 = true){
                                left(tmid)
                }
                else {
                                right(tmid)
                }  
        }
    }
);

win.loopMessage(); 
