package org.mbc.controller;

import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.GetMapping;

@Controller //  url 분기 담당
public class HomeController {
    @GetMapping("/")    // http:localhost:8000/ 반응하는 매서드
    public String home(){

        return "index";  // 요청이 온 후에 프론트를 전달한다
                         // resources/templates/index.html을 전달
    }
}
