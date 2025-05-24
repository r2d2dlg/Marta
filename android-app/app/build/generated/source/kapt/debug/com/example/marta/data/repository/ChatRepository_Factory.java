package com.example.marta.data.repository;

import com.example.marta.data.api.ApiService;
import dagger.internal.DaggerGenerated;
import dagger.internal.Factory;
import dagger.internal.QualifierMetadata;
import dagger.internal.ScopeMetadata;
import javax.annotation.processing.Generated;
import javax.inject.Provider;

@ScopeMetadata("javax.inject.Singleton")
@QualifierMetadata
@DaggerGenerated
@Generated(
    value = "dagger.internal.codegen.ComponentProcessor",
    comments = "https://dagger.dev"
)
@SuppressWarnings({
    "unchecked",
    "rawtypes",
    "KotlinInternal",
    "KotlinInternalInJava"
})
public final class ChatRepository_Factory implements Factory<ChatRepository> {
  private final Provider<ApiService> apiServiceProvider;

  public ChatRepository_Factory(Provider<ApiService> apiServiceProvider) {
    this.apiServiceProvider = apiServiceProvider;
  }

  @Override
  public ChatRepository get() {
    return newInstance(apiServiceProvider.get());
  }

  public static ChatRepository_Factory create(Provider<ApiService> apiServiceProvider) {
    return new ChatRepository_Factory(apiServiceProvider);
  }

  public static ChatRepository newInstance(ApiService apiService) {
    return new ChatRepository(apiService);
  }
}
