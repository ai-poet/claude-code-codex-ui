"use client";

import React, { useState, useEffect } from "react";
import CodeMirror from "@uiw/react-codemirror";
import { javascript } from "@codemirror/lang-javascript";
import { githubLight } from "@uiw/codemirror-theme-github";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { AlertCircle, Save, Key, Settings2 } from "lucide-react";
import { toast } from "sonner";
import { SupabaseService } from "@/lib/supabase-service";
import { useUserProfile } from "@/hooks/useUserProfile";

interface CodeAgentConfig {
    claudeCode?: {
        env?: Record<string, string>;
        credentials?: Record<string, any> | null;
    };
}

const DEFAULT_CLAUDE_ENV = {
    ANTHROPIC_API_KEY: "",
    // Add other Claude-specific env vars here if needed
};

const DEFAULT_CLAUDE_CREDENTIALS = {
    // Example structure - user can customize
};

// Helper function to check if credentials is meaningful (not empty/null/undefined)
const hasMeaningfulCredentials = (creds: any): boolean => {
    if (!creds || creds === null || creds === undefined || creds === '') {
        return false;
    }
    if (typeof creds === 'object' && Object.keys(creds).length === 0) {
        return false;
    }
    return true;
};

export function CodeAgentSettings() {
    const { profile, refreshProfile } = useUserProfile();
    const [claudeEnv, setClaudeEnv] = useState("");
    const [claudeCredentials, setClaudeCredentials] = useState("");
    const [isLoading, setIsLoading] = useState(false);
    const [errors, setErrors] = useState<{ 
        claudeEnv?: string; 
        claudeCredentials?: string; 
    }>({});

    // Load settings from profile on mount
    useEffect(() => {
        if (profile?.preferences) {
            const prefs = profile.preferences as any; // Use any for backward compatibility
            
            // Handle backward compatibility for Claude config
            let claudeConfig: any = {};
            if (prefs.claudeCode) {
                // Check if it's the new structure (has env/credentials properties)
                if (prefs.claudeCode.env || prefs.claudeCode.credentials) {
                    claudeConfig = prefs.claudeCode;
                } else {
                    // Old structure - migrate to new format
                    const { credentials, ...envVars } = prefs.claudeCode;
                    
                    claudeConfig = {
                        env: envVars,
                        credentials: hasMeaningfulCredentials(credentials) ? credentials : null
                    };
                }
            }
            
            setClaudeEnv(JSON.stringify(claudeConfig.env || DEFAULT_CLAUDE_ENV, null, 2));
            setClaudeCredentials(JSON.stringify(claudeConfig.credentials || DEFAULT_CLAUDE_CREDENTIALS, null, 2));
        } else {
            setClaudeEnv(JSON.stringify(DEFAULT_CLAUDE_ENV, null, 2));
            setClaudeCredentials(JSON.stringify(DEFAULT_CLAUDE_CREDENTIALS, null, 2));
        }
    }, [profile]);

    const validateJSON = (value: string, key: string) => {
        try {
            JSON.parse(value);
            setErrors(prev => ({ ...prev, [key]: undefined }));
            return true;
        } catch (e) {
            setErrors(prev => ({ ...prev, [key]: "Invalid JSON format" }));
            return false;
        }
    };

    const handleSave = async () => {
        // Validate all JSONs
        const isClaudeEnvValid = validateJSON(claudeEnv, "claudeEnv");
        const isClaudeCredentialsValid = validateJSON(claudeCredentials, "claudeCredentials");

        if (!isClaudeEnvValid || !isClaudeCredentialsValid) {
            toast.error("Please fix JSON errors before saving");
            return;
        }

        setIsLoading(true);
        try {
            const claudeEnvConfig = JSON.parse(claudeEnv);
            const claudeCredentialsConfig = JSON.parse(claudeCredentials);

            const preferences: CodeAgentConfig = {
                claudeCode: {
                    env: claudeEnvConfig,
                    credentials: hasMeaningfulCredentials(claudeCredentialsConfig) ? claudeCredentialsConfig : null,
                },
            };

            // Merge with existing preferences if any
            const existingPrefs = (profile?.preferences || {}) as Record<string, any>;
            
            // Clean up old Codex keys during migration
            const { codexCLI, codex, ...cleanedPrefs } = existingPrefs;
            
            const mergedPrefs = {
                ...cleanedPrefs,
                ...preferences,
            };

            await SupabaseService.updateUserProfile({ preferences: mergedPrefs });
            await refreshProfile();
            
            // Provide feedback about credentials handling
            const credentialsMessage = hasMeaningfulCredentials(claudeCredentialsConfig) 
                ? "Claude credentials will be configured" 
                : "Claude credentials are empty and will be skipped";
            
            toast.success(`Claude Code settings saved successfully. ${credentialsMessage}`);
        } catch (error) {
            console.error("Failed to save settings:", error);
            toast.error("Failed to save settings");
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="space-y-6">
            <Card>
                <CardHeader>
                    <CardTitle>Claude Code Settings</CardTitle>
                    <CardDescription>
                        Configure environment variables and credentials for Claude Code. These settings will be used when creating containers.
                    </CardDescription>
                </CardHeader>
                <CardContent className="space-y-8">
                    <Alert>
                        <AlertCircle className="h-4 w-4" />
                        <AlertDescription>
                            <strong>Important:</strong> Environment variables and credentials are stored separately. Store sensitive API keys in environment variables, and authentication configs in credentials.
                        </AlertDescription>
                    </Alert>

                    {/* Claude Code Settings */}
                    <div className="space-y-6">
                        <div className="flex items-center gap-2 pb-2 border-b">
                            <Settings2 className="w-5 h-5 text-blue-600" />
                            <h3 className="text-lg font-semibold">Claude Code Configuration</h3>
                        </div>
                        
                        {/* Claude Environment Variables */}
                        <div className="space-y-2">
                            <Label htmlFor="claude-env" className="flex items-center gap-2">
                                <Settings2 className="w-4 h-4" />
                                Environment Variables
                            </Label>
                            <div className="border rounded-lg overflow-hidden">
                                <CodeMirror
                                    id="claude-env"
                                    value={claudeEnv}
                                    height="200px"
                                    extensions={[javascript({ jsx: false })]}
                                    theme={githubLight}
                                    onChange={(value) => {
                                        setClaudeEnv(value);
                                        validateJSON(value, "claudeEnv");
                                    }}
                                    placeholder={JSON.stringify(DEFAULT_CLAUDE_ENV, null, 2)}
                                />
                            </div>
                            {errors.claudeEnv && (
                                <p className="text-sm text-red-500 mt-1">{errors.claudeEnv}</p>
                            )}
                            <p className="text-sm text-muted-foreground">
                                Configure environment variables for Claude Code CLI (@anthropic-ai/claude-code)
                            </p>
                        </div>

                        {/* Claude Credentials */}
                        <div className="space-y-2">
                            <Label htmlFor="claude-credentials" className="flex items-center gap-2">
                                <Key className="w-4 h-4" />
                                Credentials (Optional)
                            </Label>
                            <div className="border rounded-lg overflow-hidden">
                                <CodeMirror
                                    id="claude-credentials"
                                    value={claudeCredentials}
                                    height="150px"
                                    extensions={[javascript({ jsx: false })]}
                                    theme={githubLight}
                                    onChange={(value) => {
                                        setClaudeCredentials(value);
                                        validateJSON(value, "claudeCredentials");
                                    }}
                                    placeholder={JSON.stringify(DEFAULT_CLAUDE_CREDENTIALS, null, 2)}
                                />
                            </div>
                            {errors.claudeCredentials && (
                                <p className="text-sm text-red-500 mt-1">{errors.claudeCredentials}</p>
                            )}
                            <p className="text-sm text-muted-foreground">
                                Configure authentication credentials for Claude Code CLI (will be saved to ~/.claude/.credentials.json)
                            </p>
                        </div>
                    </div>

                    <Button
                        onClick={handleSave}
                        disabled={isLoading || !!errors.claudeEnv || !!errors.claudeCredentials}
                        className="w-full"
                    >
                        <Save className="w-4 h-4 mr-2" />
                        {isLoading ? "Saving..." : "Save Settings"}
                    </Button>
                </CardContent>
            </Card>
        </div>
    );
}