package org.mbc.controller.config;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

import org.springframework.web.reactive.function.client.ExchangeStrategies;
import org.springframework.web.reactive.function.client.WebClient;

@Configuration  // 환경설정용 클래스
public class WebClientConfig {
    // 이미지를 보내거나 영상을 보낼 때 데이터의 용량이 크기 때문에 버퍼 사이즈를 조절해야 한다
    // WebClient를 구성하고 반으로 정의하여 애플리케이션에서 사용할 수 있도록 함

    @Bean
    WebClient webClient(){
        return WebClient.builder().exchangeStrategies(ExchangeStrategies.builder()
                .codecs(configurer
                        -> configurer.defaultCodecs().maxInMemorySize(-1))  // 무제한 버퍼
                        .build())
                        .baseUrl("http://localhost:8000").build();  // 파이썬 경로 지정,
    }
}
