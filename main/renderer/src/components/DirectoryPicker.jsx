import React, { useState, useEffect } from 'react'

/**
 * DirectoryPicker Component
 * 
 * Provides a beautiful interface for selecting custom project directories
 * Features:
 * - Native directory browser integration
 * - Real-time path validation
 * - Directory suitability analysis 
 * - Manual path input with autocomplete-style validation
 * - Permission checks and warnings
 */
const DirectoryPicker = ({ 
  value = '',
  onChange,
  label = 'Project Directory',
  placeholder = 'Choose a directory for your project...',
  disabled = false,
  showValidation = true,
  className = ''
}) => {
  console.log('📂 [DIRECTORY_PICKER] Component rendering with value:', value)

  // Component state
  const [selectedPath, setSelectedPath] = useState(value)
  const [isValidating, setIsValidating] = useState(false)
  const [validationResult, setValidationResult] = useState(null)
  const [directoryInfo, setDirectoryInfo] = useState(null)
  const [error, setError] = useState(null)
  const [validateTimeout, setValidateTimeout] = useState(null)

  // MEMORY LEAK FIX: Cleanup timeout on unmount
  useEffect(() => {
    return () => {
      if (validateTimeout) {
        clearTimeout(validateTimeout)
        console.log('🧹 [DIRECTORY_PICKER] Cleanup: Cleared validation timeout')
      }
    }
  }, [validateTimeout])

  // Update internal state when value prop changes
  useEffect(() => {
    console.log('📂 [DIRECTORY_PICKER] Value prop changed:', value)
    setSelectedPath(value)
    
    // Validate new value
    if (value && value.trim()) {
      validateDirectory(value.trim())
    } else {
      setValidationResult(null)
      setDirectoryInfo(null)
    }
  }, [value])

  /**
   * Validate a directory path using backend validation
   */
  const validateDirectory = async (directoryPath) => {
    if (!directoryPath || !directoryPath.trim()) {
      setValidationResult(null)
      setDirectoryInfo(null)
      return
    }

    console.log('📂 [DIRECTORY_PICKER] Validating directory:', directoryPath)
    setIsValidating(true)
    setError(null)

    try {
      // Get directory info first
      const infoResponse = await window.electronAPI?.fileSystem.getDirectoryInfo(directoryPath)
      console.log('📂 [DIRECTORY_PICKER] Directory info response:', infoResponse)

      if (infoResponse && infoResponse.success) {
        setDirectoryInfo(infoResponse)
        
        // Now validate with backend
        const validationResponse = await window.electronAPI?.project.validateCustomDirectory(directoryPath)
        console.log('📂 [DIRECTORY_PICKER] Validation response:', validationResponse)
        
        // Handle WebSocket response structure
        const data = validationResponse?.data || validationResponse
        
        if (data && data.success) {
          setValidationResult(data.validation_result)
          console.log('✅ [DIRECTORY_PICKER] Validation completed:', data.validation_result)
        } else {
          throw new Error(data?.message || data?.error || 'Validation failed')
        }
      } else {
        setDirectoryInfo(null)
        setValidationResult({
          is_valid: false,
          is_suitable: false,
          errors: [infoResponse?.error || 'Directory not accessible'],
          warnings: [],
          suggestions: ['Please select an existing, accessible directory']
        })
      }
    } catch (error) {
      console.error('❌ [DIRECTORY_PICKER] Validation failed:', error)
      setError(error.message)
      setValidationResult({
        is_valid: false,
        is_suitable: false,
        errors: [error.message],
        warnings: [],
        suggestions: []
      })
    } finally {
      setIsValidating(false)
    }
  }

  /**
   * Handle native directory browser
   */
  const handleBrowseDirectory = async () => {
    console.log('📂 [DIRECTORY_PICKER] Opening directory browser...')
    console.log('📂 [DIRECTORY_PICKER] electronAPI available:', !!window.electronAPI)
    console.log('📂 [DIRECTORY_PICKER] fileSystem available:', !!window.electronAPI?.fileSystem)
    console.log('📂 [DIRECTORY_PICKER] selectDirectory available:', !!window.electronAPI?.fileSystem?.selectDirectory)
    
    // Clear any previous errors
    setError(null)
    
    try {
      if (!window.electronAPI) {
        throw new Error('electronAPI not available')
      }
      
      if (!window.electronAPI.fileSystem) {
        throw new Error('fileSystem API not available')
      }
      
      if (!window.electronAPI.fileSystem.selectDirectory) {
        throw new Error('selectDirectory method not available')
      }
      
      console.log('📂 [DIRECTORY_PICKER] Calling selectDirectory with options...')
      const result = await window.electronAPI.fileSystem.selectDirectory({
        title: 'Select Project Directory',
        defaultPath: selectedPath || undefined,
        message: 'Choose a directory where your project will be stored'
      })
      
      console.log('📂 [DIRECTORY_PICKER] Directory selection result:', result)
      
      if (result && result.success && !result.canceled) {
        const newPath = result.directory
        console.log('📂 [DIRECTORY_PICKER] Directory selected:', newPath)
        
        setSelectedPath(newPath)
        
        // Notify parent component
        if (onChange) {
          onChange(newPath)
        }
        
        // Validate the selected directory
        await validateDirectory(newPath)
      } else if (result?.canceled) {
        console.log('📂 [DIRECTORY_PICKER] Directory selection canceled by user')
      } else {
        console.log('📂 [DIRECTORY_PICKER] Directory selection failed:', result)
        setError(`Directory selection failed: ${result?.error || 'Unknown error'}`)
      }
    } catch (error) {
      console.error('❌ [DIRECTORY_PICKER] Failed to browse directory:', error)
      setError(`Failed to open directory browser: ${error.message}`)
    }
  }

  /**
   * Handle manual path input
   */
  const handlePathChange = (event) => {
    const newPath = event.target.value
    console.log('📂 [DIRECTORY_PICKER] Manual path input:', newPath)
    
    setSelectedPath(newPath)
    
    // Notify parent component immediately
    if (onChange) {
      onChange(newPath)
    }

    // Debounced validation
    if (validateTimeout) {
      clearTimeout(validateTimeout)
    }
    
    const newTimeout = setTimeout(() => {
      if (newPath && newPath.trim()) {
        validateDirectory(newPath.trim())
      } else {
        setValidationResult(null)
        setDirectoryInfo(null)
      }
    }, 500)
    
    setValidateTimeout(newTimeout)
  }

  /**
   * Get validation status styling
   */
  const getValidationStyling = () => {
    if (!validationResult) return ''
    
    if (validationResult.is_valid && validationResult.is_suitable) {
      return 'border-green-500 bg-green-50 dark:bg-green-900/20'
    } else if (validationResult.is_valid && !validationResult.is_suitable) {
      return 'border-yellow-500 bg-yellow-50 dark:bg-yellow-900/20'  
    } else {
      return 'border-red-500 bg-red-50 dark:bg-red-900/20'
    }
  }

  /**
   * Get validation icon
   */
  const getValidationIcon = () => {
    if (isValidating) return '🔄'
    if (!validationResult) return '📂'
    
    if (validationResult.is_valid && validationResult.is_suitable) {
      return '✅'
    } else if (validationResult.is_valid && !validationResult.is_suitable) {
      return '⚠️'
    } else {
      return '❌'
    }
  }

  return (
    <div className={`space-y-3 ${className}`}>
      {/* Label */}
      {label && (
        <label className="form-label">
          {label}
        </label>
      )}

      {/* Directory Input Row */}
      <div className="flex space-x-2">
        {/* Path Input */}
        <div className="flex-1 relative">
          <input
            type="text"
            value={selectedPath}
            onChange={handlePathChange}
            placeholder={placeholder}
            disabled={disabled}
            className={`form-input pr-10 ${getValidationStyling()}`}
          />
          
          {/* Validation Icon */}
          <div className="absolute right-3 top-1/2 transform -translate-y-1/2">
            <span className="text-lg">
              {getValidationIcon()}
            </span>
          </div>
        </div>

        {/* Browse Button */}
        <button
          type="button"
          onClick={handleBrowseDirectory}
          disabled={disabled || isValidating}
          className="btn-outline px-4 flex items-center space-x-2"
          title="Browse for directory"
        >
          <span>📁</span>
          <span>Browse</span>
        </button>
      </div>

      {/* Error Display */}
      {error && (
        <div className="text-sm text-red-600 dark:text-red-400 flex items-center space-x-1">
          <span>❌</span>
          <span>{error}</span>
        </div>
      )}

      {/* Validation Status */}
      {showValidation && validationResult && (
        <div className="space-y-2">
          {/* Validation Summary */}
          <div className="flex items-center space-x-2">
            <span className="text-lg">{getValidationIcon()}</span>
            <span className={`text-sm font-medium ${
              validationResult.is_valid && validationResult.is_suitable
                ? 'text-green-600 dark:text-green-400'
                : validationResult.is_valid && !validationResult.is_suitable
                ? 'text-yellow-600 dark:text-yellow-400'
                : 'text-red-600 dark:text-red-400'
            }`}>
              {validationResult.is_valid && validationResult.is_suitable
                ? 'Perfect! This directory is ideal for your project'
                : validationResult.is_valid && !validationResult.is_suitable
                ? 'Directory is valid but has some concerns'
                : 'Directory has issues that need attention'
              }
            </span>
          </div>

          {/* Directory Info */}
          {directoryInfo && (
            <div className="text-xs text-gray-600 dark:text-gray-400 bg-gray-50 dark:bg-gray-800 rounded p-2">
              <div className="grid grid-cols-2 gap-2">
                <div>📊 {directoryInfo.itemCount} items</div>
                <div>{directoryInfo.writable ? '✅ Writable' : '❌ Read-only'}</div>
                {directoryInfo.hasProjectFiles && (
                  <div className="col-span-2">
                    🔍 Found: {directoryInfo.projectFiles.join(', ')}
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Errors */}
          {validationResult.errors && validationResult.errors.length > 0 && (
            <div className="space-y-1">
              {validationResult.errors.map((error, index) => (
                <div key={index} className="text-sm text-red-600 dark:text-red-400 flex items-start space-x-1">
                  <span className="mt-0.5">❌</span>
                  <span>{error}</span>
                </div>
              ))}
            </div>
          )}

          {/* Warnings */}
          {validationResult.warnings && validationResult.warnings.length > 0 && (
            <div className="space-y-1">
              {validationResult.warnings.map((warning, index) => (
                <div key={index} className="text-sm text-yellow-600 dark:text-yellow-400 flex items-start space-x-1">
                  <span className="mt-0.5">⚠️</span>
                  <span>{warning}</span>
                </div>
              ))}
            </div>
          )}

          {/* Suggestions */}
          {validationResult.suggestions && validationResult.suggestions.length > 0 && (
            <div className="space-y-1">
              {validationResult.suggestions.map((suggestion, index) => (
                <div key={index} className="text-sm text-blue-600 dark:text-blue-400 flex items-start space-x-1">
                  <span className="mt-0.5">💡</span>
                  <span>{suggestion}</span>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Loading State */}
      {isValidating && (
        <div className="text-sm text-gray-500 dark:text-gray-400 flex items-center space-x-2">
          <span>🔄</span>
          <span>Validating directory...</span>
        </div>
      )}
    </div>
  )
}

export default DirectoryPicker 