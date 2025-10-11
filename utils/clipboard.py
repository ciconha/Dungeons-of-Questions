# utils/clipboard.py
import platform
import subprocess
import os

class SimpleClipboard:
    """Sistema de clipboard multiplataforma simples"""
    
    @staticmethod
    def get_clipboard():
        """Obtém texto da área de transferência"""
        system = platform.system()
        
        try:
            if system == "Windows":
                # Windows
                import win32clipboard
                win32clipboard.OpenClipboard()
                try:
                    data = win32clipboard.GetClipboardData(win32clipboard.CF_TEXT)
                    return data.decode('latin-1')
                except:
                    return ""
                finally:
                    win32clipboard.CloseClipboard()
                    
            elif system == "Darwin":
                # macOS
                process = subprocess.Popen(['pbpaste'], stdout=subprocess.PIPE)
                result, _ = process.communicate()
                return result.decode('utf-8')
                
            else:
                # Linux e outros
                try:
                    # Tenta xclip primeiro
                    process = subprocess.Popen(['xclip', '-selection', 'clipboard', '-o'], 
                                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    result, error = process.communicate()
                    if process.returncode == 0:
                        return result.decode('utf-8')
                    
                    # Tenta xsel se xclip falhar
                    process = subprocess.Popen(['xsel', '--clipboard', '--output'], 
                                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    result, error = process.communicate()
                    if process.returncode == 0:
                        return result.decode('utf-8')
                        
                except:
                    pass
                return ""
                
        except Exception as e:
            print(f"❌ Erro ao acessar clipboard: {e}")
            return ""
    
    @staticmethod
    def set_clipboard(text):
        """Define texto na área de transferência"""
        system = platform.system()
        
        try:
            if system == "Windows":
                import win32clipboard
                win32clipboard.OpenClipboard()
                win32clipboard.EmptyClipboard()
                win32clipboard.SetClipboardText(text)
                win32clipboard.CloseClipboard()
                
            elif system == "Darwin":
                process = subprocess.Popen(['pbcopy'], stdin=subprocess.PIPE)
                process.communicate(input=text.encode('utf-8'))
                
            else:
                # Linux e outros
                try:
                    process = subprocess.Popen(['xclip', '-selection', 'clipboard'], 
                                             stdin=subprocess.PIPE)
                    process.communicate(input=text.encode('utf-8'))
                except:
                    try:
                        process = subprocess.Popen(['xsel', '--clipboard', '--input'], 
                                                 stdin=subprocess.PIPE)
                        process.communicate(input=text.encode('utf-8'))
                    except:
                        pass
                        
        except Exception as e:
            print(f"❌ Erro ao definir clipboard: {e}")

# Instância global
clipboard = SimpleClipboard()