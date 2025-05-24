package com.example.marta.di;

import com.example.marta.data.api.ApiClient;
import dagger.internal.DaggerGenerated;
import dagger.internal.Factory;
import dagger.internal.Preconditions;
import dagger.internal.QualifierMetadata;
import dagger.internal.ScopeMetadata;
import javax.annotation.processing.Generated;

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
public final class NetworkModule_ProvideApiClientFactory implements Factory<ApiClient> {
  @Override
  public ApiClient get() {
    return provideApiClient();
  }

  public static NetworkModule_ProvideApiClientFactory create() {
    return InstanceHolder.INSTANCE;
  }

  public static ApiClient provideApiClient() {
    return Preconditions.checkNotNullFromProvides(NetworkModule.INSTANCE.provideApiClient());
  }

  private static final class InstanceHolder {
    private static final NetworkModule_ProvideApiClientFactory INSTANCE = new NetworkModule_ProvideApiClientFactory();
  }
}
