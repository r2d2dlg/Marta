package com.example.marta

import android.os.Build
import android.os.Bundle
import android.view.View
import android.view.WindowInsetsController
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.WindowInsets
import androidx.compose.foundation.layout.WindowInsetsSides
import androidx.compose.foundation.layout.only
import androidx.compose.foundation.layout.safeDrawing
import androidx.compose.foundation.layout.windowInsetsPadding
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.runtime.Composable
import androidx.compose.runtime.SideEffect
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.toArgb
import androidx.core.view.WindowCompat
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.rememberNavController
import com.example.marta.ui.chat.ChatScreen
import com.example.marta.ui.theme.MartaTheme
import dagger.hilt.android.AndroidEntryPoint

@AndroidEntryPoint
class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        
        // Enable edge-to-edge display
        WindowCompat.setDecorFitsSystemWindows(window, false)
        
        setContent {
            // System UI controller is now handled by MartaTheme
            // val systemUiController = rememberSystemUiController() // Removed
            // val useDarkIcons = MaterialTheme.colorScheme.isLight // Removed
            
            // Set the status bar and navigation bar colors
            // SideEffect { // Removed
            //     systemUiController.setSystemBarsColor(
            //         color = Color.Transparent,
            //         darkIcons = useDarkIcons,
            //         isNavigationBarContrastEnforced = false
            //     )
            // } // Removed
            
            MartaApp()
        }
    }
}

@Composable
fun MartaApp() {
    val navController = rememberNavController()
    
    MartaTheme {
        Surface(
            modifier = Modifier
                .fillMaxSize()
                .windowInsetsPadding(
                    WindowInsets.safeDrawing.only(
                        WindowInsetsSides.Horizontal + WindowInsetsSides.Top
                    )
                ),
            color = MaterialTheme.colorScheme.background
        ) {
            NavHost(
                navController = navController,
                startDestination = "chat"
            ) {
                composable("chat") {
                    ChatScreen(
                        onNavigateBack = { /* Handle back press if needed */ }
                    )
                }
                // Add more destinations here
            }
        }
    }
}
